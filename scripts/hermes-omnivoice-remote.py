#!/usr/bin/env python3
"""Hermes command-provider wrapper for a remote OmniVoice FastAPI service."""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
from pathlib import Path
import re
import socket
import sys
import tempfile
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit
import ipaddress


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
    re.compile(r"(Authorization:\s*)[^\r\n]+", re.IGNORECASE),
]


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


def request_audio(
    *,
    url: str,
    token: str,
    text: str,
    voice: str,
    speed: float,
    audio_format: str,
    model: str,
    language: str,
    timeout: float,
) -> tuple[bytes, str]:
    payload: dict[str, object] = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": audio_format,
        "speed": speed,
    }
    if language:
        payload["language_id"] = language
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": f"audio/{audio_format}, audio/*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "hermes-omnivoice-remote/1",
    }
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
            return data, content_type
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


def run(argv: list[str] | None = None, env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call remote OmniVoice FastAPI for Hermes TTS")
    parser.add_argument("--text-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--speed", default="1.0")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--api-token", default="")
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
        timeout = parse_positive_float(str(args.timeout), "timeout")
        speed = parse_positive_float(args.speed, "speed")
        max_chars = parse_positive_int(args.max_chars, "max chars")
        if not args.voice.strip():
            raise RemoteOmniVoiceError("voice must not be empty")
        if not args.model.strip():
            raise RemoteOmniVoiceError("model must not be empty")
        token = args.api_token or runtime_env.get("OMNIVOICE_REMOTE_API_TOKEN", "")
        if not token.strip():
            raise RemoteOmniVoiceError(
                "API token is required; set --api-token or OMNIVOICE_REMOTE_API_TOKEN"
            )
        allow_public = (
            args.allow_public_base_url
            or runtime_env.get("OMNIVOICE_REMOTE_ALLOW_PUBLIC") == "1"
        )
        base_url = normalize_base_url(
            args.base_url or runtime_env.get("OMNIVOICE_REMOTE_BASE_URL", ""),
            allow_public,
        )
        url = join_url(base_url, args.speech_path)
        text = read_text_file(args.text_file, max_chars)
        data, content_type = request_audio(
            url=url,
            token=token.strip(),
            text=text,
            voice=args.voice.strip(),
            speed=speed,
            audio_format=args.format,
            model=args.model.strip(),
            language=args.language.strip(),
            timeout=timeout,
        )
        validate_audio_response(data, content_type, args.format)
        write_output(args.out, data, args.format)
    except (OSError, RemoteOmniVoiceError) as exc:
        return fail(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(run())
