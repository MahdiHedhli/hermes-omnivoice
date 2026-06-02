#!/usr/bin/env python3
"""Hermes command-provider wrapper for a remote OmniVoice FastAPI service."""

from __future__ import annotations

import argparse
import contextlib
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import socket
import stat
import struct
import subprocess
import sys
import tempfile
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit


TRANSPORTS = {"http", "ssh-loopback"}
AUDIO_EXTENSIONS = {
    "wav": ".wav",
    "mp3": ".mp3",
    "flac": ".flac",
    "ogg": ".ogg",
    "opus": ".opus",
}
AUDIO_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/flac",
    "audio/ogg",
    "audio/opus",
    "application/octet-stream",
}
TOKEN_PATTERNS = [
    re.compile(r"(Bearer\s+)[A-Za-z0-9._~+/=-]+", re.IGNORECASE),
    re.compile(r"(OMNIVOICE_REMOTE_API_TOKEN=)[^\s]+"),
    re.compile(r"(OMNIVOICE_REMOTE_TOKEN_FILE=)[^\s]+"),
    re.compile(r"(Authorization:\s*)[^\r\n]+", re.IGNORECASE),
    re.compile(r'("token"\s*:\s*")[^"]+(?=")', re.IGNORECASE),
]
REMOTE_HTTP_SCRIPT = r"""
from __future__ import annotations

import json
import socket
import struct
import sys
from urllib import error, request


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


try:
    envelope = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    method = envelope["method"]
    url = envelope["url"]
    token = envelope["token"]
    timeout = float(envelope["timeout"])
    payload = envelope.get("payload")
    accept = envelope.get("accept", "audio/*")
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": accept,
        "Authorization": f"Bearer {token}",
        "User-Agent": "hermes-omnivoice-remote-ssh-loopback/1",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            response_body = response.read()
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "")
    except error.HTTPError as exc:
        if exc.code in {401, 403}:
            die(f"loopback service rejected authentication: HTTP {exc.code}", 12)
        die(f"loopback service returned HTTP {exc.code}", 13)
    except (error.URLError, TimeoutError, socket.timeout) as exc:
        reason = getattr(exc, "reason", exc)
        die(f"loopback service request failed: {reason}", 14)

    meta = json.dumps(
        {"status": status, "content_type": content_type},
        separators=(",", ":"),
    ).encode("utf-8")
    sys.stdout.buffer.write(struct.pack(">I", len(meta)))
    sys.stdout.buffer.write(meta)
    sys.stdout.buffer.write(response_body)
except SystemExit:
    raise
except Exception as exc:
    die(f"ssh loopback helper failed: {exc}", 15)
"""


class RemoteOmniVoiceError(RuntimeError):
    """Raised for clean user-facing remote wrapper failures."""


def redact(value: str) -> str:
    redacted = value
    for pattern in TOKEN_PATTERNS:
        redacted = pattern.sub(r"\1<redacted>", redacted)
    return redacted


def fail(message: str) -> int:
    print(f"hermes-omnivoice-remote: {redact(message)}", file=sys.stderr)
    return 1


def parse_transport(value: str) -> str:
    transport = (value or "http").strip().lower()
    if transport not in TRANSPORTS:
        raise RemoteOmniVoiceError(
            f"transport must be one of {', '.join(sorted(TRANSPORTS))}"
        )
    return transport


def parse_positive_float(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RemoteOmniVoiceError(f"{name} must be a finite number greater than 0") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise RemoteOmniVoiceError(f"{name} must be a finite number greater than 0")
    return parsed


def parse_positive_int(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if value <= 0:
        raise RemoteOmniVoiceError(f"{name} must be greater than 0")
    return value


def parse_ssh_port(value: str | int, name: str = "SSH port") -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RemoteOmniVoiceError(f"{name} must be an integer") from exc
    if parsed < 1 or parsed > 65535:
        raise RemoteOmniVoiceError(f"{name} must be between 1 and 65535")
    return parsed


def host_is_allowed(host: str, allow_public: bool) -> bool:
    if allow_public:
        return True
    normalized = host.rstrip(".").lower()
    if normalized in {"localhost", "::1"}:
        return True
    if normalized.endswith((".localhost", ".local", ".ts.net")):
        return True
    if "." not in normalized and ":" not in normalized:
        return True
    try:
        ip = ipaddress.ip_address(normalized.strip("[]"))
    except ValueError:
        return False
    tailscale_cgnat = ipaddress.ip_network("100.64.0.0/10")
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip in tailscale_cgnat
    )


def host_is_loopback(host: str) -> bool:
    normalized = host.rstrip(".").lower()
    if normalized in {"localhost", "::1"} or normalized.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(normalized.strip("[]")).is_loopback
    except ValueError:
        return False


def normalize_base_url(raw_url: str, allow_public: bool) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise RemoteOmniVoiceError(
            "base URL is required; set --base-url or OMNIVOICE_REMOTE_BASE_URL"
        )
    parts = urlsplit(raw_url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise RemoteOmniVoiceError("base URL must be an absolute http(s) URL")
    if parts.username or parts.password:
        raise RemoteOmniVoiceError("base URL must not include userinfo")
    if parts.query or parts.fragment:
        raise RemoteOmniVoiceError("base URL must not include query or fragment")
    host = parts.hostname or ""
    if not host_is_allowed(host, allow_public):
        raise RemoteOmniVoiceError(
            "refusing public remote base URL; use OMNIVOICE_REMOTE_ALLOW_PUBLIC=1 "
            "only after adding authentication and network review"
        )
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def normalize_loopback_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise RemoteOmniVoiceError("remote loopback URL is required")
    parts = urlsplit(raw_url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise RemoteOmniVoiceError("remote loopback URL must be an absolute http(s) URL")
    if parts.username or parts.password:
        raise RemoteOmniVoiceError("remote loopback URL must not include userinfo")
    if parts.query or parts.fragment:
        raise RemoteOmniVoiceError("remote loopback URL must not include query or fragment")
    if not host_is_loopback(parts.hostname or ""):
        raise RemoteOmniVoiceError(
            "ssh-loopback mode requires a loopback remote URL such as http://127.0.0.1:8880"
        )
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def join_url(base_url: str, endpoint_path: str) -> str:
    if not endpoint_path.startswith("/"):
        endpoint_path = f"/{endpoint_path}"
    return f"{base_url.rstrip('/')}{endpoint_path}"


def read_text_file(path: Path, max_chars: int | None) -> str:
    path = path.expanduser()
    if not path.is_file():
        raise RemoteOmniVoiceError(f"text file does not exist: {path}")
    if path.is_symlink():
        raise RemoteOmniVoiceError("text file cannot be a symlink")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise RemoteOmniVoiceError("text must not be empty")
    if max_chars is not None and len(text) > max_chars:
        raise RemoteOmniVoiceError(f"text file exceeds max text length: {len(text)} > {max_chars}")
    return text


def read_token_file(path: Path) -> str:
    path = path.expanduser()
    if not path.is_file():
        raise RemoteOmniVoiceError(f"token file does not exist: {path}")
    if path.is_symlink():
        raise RemoteOmniVoiceError("token file cannot be a symlink")
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise RemoteOmniVoiceError("token file must not be group/world-accessible")
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise RemoteOmniVoiceError("token file is empty")
    return token


def resolve_api_token(token_file: str, api_token: str, env: dict[str, str]) -> str:
    token_file_value = token_file or env.get("OMNIVOICE_REMOTE_TOKEN_FILE", "")
    if token_file_value:
        return read_token_file(Path(token_file_value))
    token = api_token or env.get("OMNIVOICE_REMOTE_API_TOKEN", "")
    if not token.strip():
        raise RemoteOmniVoiceError(
            "API token is required; set --token-file, OMNIVOICE_REMOTE_TOKEN_FILE, "
            "--api-token, or OMNIVOICE_REMOTE_API_TOKEN"
        )
    return token.strip()


def validate_ssh_host(host: str) -> str:
    host = host.strip()
    if not host:
        raise RemoteOmniVoiceError(
            "SSH host is required for ssh-loopback mode; set --ssh-host or "
            "OMNIVOICE_REMOTE_SSH_HOST"
        )
    if any(char.isspace() for char in host):
        raise RemoteOmniVoiceError("SSH host must not contain whitespace")
    return host


def normalize_optional_identity_file(raw_path: str) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if not path.is_file():
        raise RemoteOmniVoiceError(f"SSH identity file does not exist: {path}")
    if path.is_symlink():
        raise RemoteOmniVoiceError("SSH identity file cannot be a symlink")
    return path


def wav_is_valid(data: bytes) -> bool:
    return len(data) >= 44 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"


def looks_like_audio(data: bytes, audio_format: str) -> bool:
    if audio_format == "wav":
        return wav_is_valid(data)
    if audio_format == "flac":
        return data.startswith(b"fLaC")
    if audio_format == "ogg" or audio_format == "opus":
        return data.startswith(b"OggS")
    if audio_format == "mp3":
        return data.startswith(b"ID3") or data[:2] == b"\xff\xfb"
    return False


def validate_audio_response(data: bytes, content_type: str, audio_format: str) -> None:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if not data:
        raise RemoteOmniVoiceError("remote service returned empty audio")
    if looks_like_audio(data, audio_format):
        return
    if media_type in AUDIO_CONTENT_TYPES and media_type.startswith("audio/") and len(data) > 32:
        return
    raise RemoteOmniVoiceError(
        f"remote service did not return valid {audio_format} audio"
    )


def write_output(path: Path, data: bytes, audio_format: str) -> None:
    path = path.expanduser()
    expected_suffix = AUDIO_EXTENSIONS[audio_format]
    if path.suffix.lower() != expected_suffix:
        raise RemoteOmniVoiceError(f"output path must use {expected_suffix} extension")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.is_dir():
        raise RemoteOmniVoiceError(f"output path is a directory: {path}")
    if path.is_symlink():
        path.unlink()
    handle = tempfile.NamedTemporaryFile(
        mode="wb",
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        delete=False,
    )
    tmp_path = Path(handle.name)
    try:
        with handle:
            handle.write(data)
        tmp_path.chmod(0o600)
        tmp_path.replace(path)
        path.chmod(0o600)
    except OSError:
        with contextlib.suppress(OSError):
            tmp_path.unlink()
        raise


def build_speech_payload(
    *,
    text: str,
    voice: str,
    speed: float,
    audio_format: str,
    model: str,
    language: str,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": audio_format,
        "speed": speed,
    }
    if language:
        payload["language_id"] = language
    return payload


def request_http(
    *,
    url: str,
    token: str,
    method: str,
    payload: dict[str, object] | None,
    accept: str,
    timeout: float,
) -> tuple[int, bytes, str]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": accept,
        "Authorization": f"Bearer {token}",
        "User-Agent": "hermes-omnivoice-remote/1",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
            return getattr(response, "status", 200), data, content_type
    except error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", errors="replace").strip()
        detail = redact(detail).replace(token, "<redacted>")
        if exc.code in {401, 403}:
            raise RemoteOmniVoiceError(f"remote service rejected authentication: HTTP {exc.code}")
        raise RemoteOmniVoiceError(
            f"remote service returned HTTP {exc.code}"
            + (f": {detail}" if detail else "")
        ) from exc
    except (error.URLError, TimeoutError, socket.timeout) as exc:
        reason = getattr(exc, "reason", exc)
        raise RemoteOmniVoiceError(f"remote service request failed: {reason}") from exc


def request_audio(
    *,
    url: str,
    token: str,
    payload: dict[str, object],
    audio_format: str,
    timeout: float,
) -> tuple[bytes, str]:
    _status, data, content_type = request_http(
        url=url,
        token=token,
        method="POST",
        payload=payload,
        accept=f"audio/{audio_format}, audio/*",
        timeout=timeout,
    )
    return data, content_type


def request_health(
    *,
    url: str,
    token: str,
    timeout: float,
) -> tuple[int, bytes, str]:
    return request_http(
        url=url,
        token=token,
        method="GET",
        payload=None,
        accept="application/json",
        timeout=timeout,
    )


def build_ssh_command(
    *,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
    timeout: float,
) -> list[str]:
    connect_timeout = max(1, min(int(math.ceil(timeout)), 30))
    command = [
        "ssh",
        "-p",
        str(ssh_port),
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
    ]
    if ssh_identity_file is not None:
        command.extend(["-i", str(ssh_identity_file)])
    command.extend([ssh_host, "python3", "-c", REMOTE_HTTP_SCRIPT])
    return command


def request_ssh_loopback(
    *,
    url: str,
    token: str,
    method: str,
    payload: dict[str, object] | None,
    accept: str,
    timeout: float,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
) -> tuple[int, bytes, str]:
    envelope = json.dumps(
        {
            "method": method,
            "url": url,
            "token": token,
            "payload": payload,
            "accept": accept,
            "timeout": timeout,
        }
    ).encode("utf-8")
    command = build_ssh_command(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity_file,
        timeout=timeout,
    )
    try:
        completed = subprocess.run(
            command,
            input=envelope,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 30,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RemoteOmniVoiceError("ssh executable not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise RemoteOmniVoiceError("ssh loopback request timed out") from exc

    stderr = completed.stderr.decode("utf-8", errors="replace").strip()
    stderr = redact(stderr).replace(token, "<redacted>")
    if completed.returncode != 0:
        raise RemoteOmniVoiceError(
            f"ssh loopback request failed with exit code {completed.returncode}"
            + (f": {stderr}" if stderr else "")
        )

    stdout = completed.stdout
    if len(stdout) < 4:
        raise RemoteOmniVoiceError("ssh loopback helper returned an invalid response")
    metadata_size = struct.unpack(">I", stdout[:4])[0]
    metadata_end = 4 + metadata_size
    if metadata_size <= 0 or len(stdout) < metadata_end:
        raise RemoteOmniVoiceError("ssh loopback helper returned truncated metadata")
    try:
        metadata = json.loads(stdout[4:metadata_end].decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RemoteOmniVoiceError("ssh loopback helper returned invalid metadata") from exc
    status = int(metadata.get("status", 200))
    content_type = str(metadata.get("content_type", ""))
    return status, stdout[metadata_end:], content_type


def request_audio_ssh_loopback(
    *,
    url: str,
    token: str,
    payload: dict[str, object],
    audio_format: str,
    timeout: float,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
) -> tuple[bytes, str]:
    status, data, content_type = request_ssh_loopback(
        url=url,
        token=token,
        method="POST",
        payload=payload,
        accept=f"audio/{audio_format}, audio/*",
        timeout=timeout,
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity_file,
    )
    if status != 200:
        raise RemoteOmniVoiceError(f"loopback service returned HTTP {status}")
    return data, content_type


def request_health_ssh_loopback(
    *,
    url: str,
    token: str,
    timeout: float,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
) -> tuple[int, bytes, str]:
    return request_ssh_loopback(
        url=url,
        token=token,
        method="GET",
        payload=None,
        accept="application/json",
        timeout=timeout,
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity_file,
    )


def synthesize(
    *,
    transport: str,
    http_base_url: str,
    remote_loopback_url: str,
    token: str,
    text: str,
    voice: str,
    speed: float,
    audio_format: str,
    model: str,
    language: str,
    timeout: float,
    speech_path: str,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
    allow_public_base_url: bool,
) -> tuple[bytes, str]:
    payload = build_speech_payload(
        text=text,
        voice=voice,
        speed=speed,
        audio_format=audio_format,
        model=model,
        language=language,
    )
    if transport == "http":
        base_url = normalize_base_url(http_base_url, allow_public_base_url)
        return request_audio(
            url=join_url(base_url, speech_path),
            token=token,
            payload=payload,
            audio_format=audio_format,
            timeout=timeout,
        )

    loopback_base_url = normalize_loopback_url(remote_loopback_url)
    return request_audio_ssh_loopback(
        url=join_url(loopback_base_url, speech_path),
        token=token,
        payload=payload,
        audio_format=audio_format,
        timeout=timeout,
        ssh_host=validate_ssh_host(ssh_host),
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity_file,
    )


def health_check(
    *,
    transport: str,
    http_base_url: str,
    remote_loopback_url: str,
    token: str,
    timeout: float,
    health_path: str,
    ssh_host: str,
    ssh_port: int,
    ssh_identity_file: Path | None,
    allow_public_base_url: bool,
) -> tuple[int, bytes, str]:
    if transport == "http":
        base_url = normalize_base_url(http_base_url, allow_public_base_url)
        return request_health(
            url=join_url(base_url, health_path),
            token=token,
            timeout=timeout,
        )
    loopback_base_url = normalize_loopback_url(remote_loopback_url)
    return request_health_ssh_loopback(
        url=join_url(loopback_base_url, health_path),
        token=token,
        timeout=timeout,
        ssh_host=validate_ssh_host(ssh_host),
        ssh_port=ssh_port,
        ssh_identity_file=ssh_identity_file,
    )


def run(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call remote OmniVoice FastAPI for Hermes TTS")
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--speed", default="1.0")
    parser.add_argument("--transport", choices=sorted(TRANSPORTS), default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--api-token", default="")
    parser.add_argument("--token-file", default="")
    parser.add_argument("--ssh-host", default="")
    parser.add_argument("--ssh-port", default="")
    parser.add_argument("--ssh-identity-file", default="")
    parser.add_argument("--remote-url", default="")
    parser.add_argument("--format", default="wav", choices=sorted(AUDIO_EXTENSIONS))
    parser.add_argument("--timeout", default=600, type=float)
    parser.add_argument("--max-chars", default=None, type=int)
    parser.add_argument("--model", default="omnivoice")
    parser.add_argument("--language", default="")
    parser.add_argument("--speech-path", default="/v1/audio/speech")
    parser.add_argument("--allow-public-base-url", action="store_true")
    args = parser.parse_args(argv)

    runtime_env = dict(os.environ if env is None else env)
    try:
        transport = parse_transport(
            args.transport or runtime_env.get("OMNIVOICE_REMOTE_TRANSPORT", "http")
        )
        timeout = parse_positive_float(str(args.timeout), "timeout")
        speed = parse_positive_float(args.speed, "speed")
        max_chars = parse_positive_int(args.max_chars, "max chars")
        ssh_port = parse_ssh_port(
            args.ssh_port or runtime_env.get("OMNIVOICE_REMOTE_SSH_PORT", "22")
        )
        if not args.voice.strip():
            raise RemoteOmniVoiceError("voice must not be empty")
        if not args.model.strip():
            raise RemoteOmniVoiceError("model must not be empty")
        token = resolve_api_token(args.token_file, args.api_token, runtime_env)
        allow_public = (
            args.allow_public_base_url
            or runtime_env.get("OMNIVOICE_REMOTE_ALLOW_PUBLIC") == "1"
        )
        text = read_text_file(args.text_file, max_chars)
        data, content_type = synthesize(
            transport=transport,
            http_base_url=args.base_url or runtime_env.get("OMNIVOICE_REMOTE_BASE_URL", ""),
            remote_loopback_url=(
                args.remote_url
                or runtime_env.get("OMNIVOICE_REMOTE_LOOPBACK_URL", "")
                or "http://127.0.0.1:8880"
            ),
            token=token.strip(),
            text=text,
            voice=args.voice.strip(),
            speed=speed,
            audio_format=args.format,
            model=args.model.strip(),
            language=args.language.strip(),
            timeout=timeout,
            speech_path=args.speech_path,
            ssh_host=args.ssh_host or runtime_env.get("OMNIVOICE_REMOTE_SSH_HOST", ""),
            ssh_port=ssh_port,
            ssh_identity_file=normalize_optional_identity_file(
                args.ssh_identity_file
                or runtime_env.get("OMNIVOICE_REMOTE_SSH_IDENTITY_FILE", "")
            ),
            allow_public_base_url=allow_public,
        )
        validate_audio_response(data, content_type, args.format)
        write_output(args.out, data, args.format)
    except (OSError, RemoteOmniVoiceError) as exc:
        return fail(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(run())
