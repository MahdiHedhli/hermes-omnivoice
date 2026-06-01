from __future__ import annotations

import contextlib
import http.server
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import unittest.mock
import wave


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hermes-omnivoice-tts.py"
PYTHON_ADAPTER_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "hermes-omnivoice-python-adapter.py"
)
SETUP_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "setup-omnivoice-python-env.py"
)
IMPORT_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "import-omnivoice-studio-voice.py"
)
VOICES_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "hermes-omnivoice-voices.py"
)
CREATE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "create-omnivoice-voice.py"
)
CHECK_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "check-omnivoice-runtime.py"
)
INSTALL_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "install-hermes-omnivoice-bridge.py"
)
STUDIO_LOCAL_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "omnivoice-studio-local.py"
)
FIND_SOURCE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "find-hermes-source.py"
)
ACCEPTANCE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "omnivoice-acceptance.py"
)
ARTIFACTS_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "check-omnivoice-artifacts.py"
)
VALIDATE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "validate-omnivoice-bridge.sh"
)
FAKE_BACKEND_PATH = Path(__file__).resolve().parent / "fixtures" / "fake_omnivoice_backend.py"
EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
SPEC = importlib.util.spec_from_file_location("hermes_omnivoice_tts", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
omnivoice = importlib.util.module_from_spec(SPEC)
sys.modules["hermes_omnivoice_tts"] = omnivoice
SPEC.loader.exec_module(omnivoice)

PYTHON_ADAPTER_SPEC = importlib.util.spec_from_file_location(
    "hermes_omnivoice_python_adapter", PYTHON_ADAPTER_SCRIPT_PATH
)
assert PYTHON_ADAPTER_SPEC is not None and PYTHON_ADAPTER_SPEC.loader is not None
python_adapter = importlib.util.module_from_spec(PYTHON_ADAPTER_SPEC)
sys.modules["hermes_omnivoice_python_adapter"] = python_adapter
PYTHON_ADAPTER_SPEC.loader.exec_module(python_adapter)

SETUP_SPEC = importlib.util.spec_from_file_location(
    "setup_omnivoice_python_env", SETUP_SCRIPT_PATH
)
assert SETUP_SPEC is not None and SETUP_SPEC.loader is not None
setup_env = importlib.util.module_from_spec(SETUP_SPEC)
sys.modules["setup_omnivoice_python_env"] = setup_env
SETUP_SPEC.loader.exec_module(setup_env)

IMPORT_SPEC = importlib.util.spec_from_file_location(
    "import_omnivoice_studio_voice", IMPORT_SCRIPT_PATH
)
assert IMPORT_SPEC is not None and IMPORT_SPEC.loader is not None
studio_import = importlib.util.module_from_spec(IMPORT_SPEC)
sys.modules["import_omnivoice_studio_voice"] = studio_import
IMPORT_SPEC.loader.exec_module(studio_import)

VOICES_SPEC = importlib.util.spec_from_file_location("hermes_omnivoice_voices", VOICES_SCRIPT_PATH)
assert VOICES_SPEC is not None and VOICES_SPEC.loader is not None
voices_cli = importlib.util.module_from_spec(VOICES_SPEC)
sys.modules["hermes_omnivoice_voices"] = voices_cli
VOICES_SPEC.loader.exec_module(voices_cli)

CREATE_SPEC = importlib.util.spec_from_file_location("create_omnivoice_voice", CREATE_SCRIPT_PATH)
assert CREATE_SPEC is not None and CREATE_SPEC.loader is not None
create_voice = importlib.util.module_from_spec(CREATE_SPEC)
sys.modules["create_omnivoice_voice"] = create_voice
CREATE_SPEC.loader.exec_module(create_voice)

CHECK_SPEC = importlib.util.spec_from_file_location("check_omnivoice_runtime", CHECK_SCRIPT_PATH)
assert CHECK_SPEC is not None and CHECK_SPEC.loader is not None
runtime_check = importlib.util.module_from_spec(CHECK_SPEC)
sys.modules["check_omnivoice_runtime"] = runtime_check
CHECK_SPEC.loader.exec_module(runtime_check)

INSTALL_SPEC = importlib.util.spec_from_file_location(
    "install_hermes_omnivoice_bridge", INSTALL_SCRIPT_PATH
)
assert INSTALL_SPEC is not None and INSTALL_SPEC.loader is not None
installer = importlib.util.module_from_spec(INSTALL_SPEC)
sys.modules["install_hermes_omnivoice_bridge"] = installer
INSTALL_SPEC.loader.exec_module(installer)

STUDIO_LOCAL_SPEC = importlib.util.spec_from_file_location(
    "omnivoice_studio_local", STUDIO_LOCAL_SCRIPT_PATH
)
assert STUDIO_LOCAL_SPEC is not None and STUDIO_LOCAL_SPEC.loader is not None
studio_local = importlib.util.module_from_spec(STUDIO_LOCAL_SPEC)
sys.modules["omnivoice_studio_local"] = studio_local
STUDIO_LOCAL_SPEC.loader.exec_module(studio_local)

FIND_SOURCE_SPEC = importlib.util.spec_from_file_location(
    "find_hermes_source", FIND_SOURCE_SCRIPT_PATH
)
assert FIND_SOURCE_SPEC is not None and FIND_SOURCE_SPEC.loader is not None
source_finder = importlib.util.module_from_spec(FIND_SOURCE_SPEC)
sys.modules["find_hermes_source"] = source_finder
FIND_SOURCE_SPEC.loader.exec_module(source_finder)

ACCEPTANCE_SPEC = importlib.util.spec_from_file_location(
    "omnivoice_acceptance", ACCEPTANCE_SCRIPT_PATH
)
assert ACCEPTANCE_SPEC is not None and ACCEPTANCE_SPEC.loader is not None
acceptance = importlib.util.module_from_spec(ACCEPTANCE_SPEC)
sys.modules["omnivoice_acceptance"] = acceptance
ACCEPTANCE_SPEC.loader.exec_module(acceptance)

ARTIFACTS_SPEC = importlib.util.spec_from_file_location(
    "check_omnivoice_artifacts", ARTIFACTS_SCRIPT_PATH
)
assert ARTIFACTS_SPEC is not None and ARTIFACTS_SPEC.loader is not None
artifact_check = importlib.util.module_from_spec(ARTIFACTS_SPEC)
sys.modules["check_omnivoice_artifacts"] = artifact_check
ARTIFACTS_SPEC.loader.exec_module(artifact_check)


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 160)


def path_mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 160)
    return buffer.getvalue()


def write_voice(root: Path, voice_id: str = "marvin", **overrides: str) -> Path:
    voice_dir = root / voice_id
    voice_dir.mkdir(parents=True)
    write_wav(voice_dir / "ref.wav")
    consent_status = overrides.get("consent_status", "confirmed")
    ref_audio = overrides.get("ref_audio", "ref.wav")
    body = f"""id: {voice_id}
name: Marvin
engine: omnivoice
mode: clone
ref_audio: {ref_audio}
ref_text: "Reference transcript for the voice sample."
language: en
speed: 1.0
consent:
  status: {consent_status}
  source: user_uploaded
  allowed_uses:
    - personal_assistant
    - local_generation
"""
    (voice_dir / "voice.yaml").write_text(body, encoding="utf-8")
    return voice_dir


def write_design_voice(root: Path, voice_id: str = "narrator", studio_profile_id: str = "") -> Path:
    voice_dir = root / voice_id
    voice_dir.mkdir(parents=True)
    studio_line = f"studio_profile_id: {studio_profile_id}\n" if studio_profile_id else ""
    body = f"""id: {voice_id}
name: Narrator
engine: omnivoice
mode: design
instruct: "male, american accent, moderate pitch"
language: en
speed: 1.0
{studio_line}consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
    - local_generation
"""
    (voice_dir / "voice.yaml").write_text(body, encoding="utf-8")
    return voice_dir


class FakeOmniVoiceModel:
    captured_load: dict = {}
    captured_generate: dict = {}
    sampling_rate = 24000

    @classmethod
    def from_pretrained(cls, model: str, **kwargs):
        cls.captured_load = {"model": model, **kwargs}
        return cls()

    def generate(self, **kwargs):
        type(self).captured_generate = kwargs
        return [[0.0, 0.0, 0.0]]


@contextlib.contextmanager
def fake_omnivoice_python_modules():
    FakeOmniVoiceModel.captured_load = {}
    FakeOmniVoiceModel.captured_generate = {}
    FakeOmniVoiceModel.sampling_rate = 24000

    omnivoice_module = types.ModuleType("omnivoice")
    models_module = types.ModuleType("omnivoice.models")
    model_module = types.ModuleType("omnivoice.models.omnivoice")
    model_module.OmniVoice = FakeOmniVoiceModel
    soundfile_module = types.ModuleType("soundfile")
    soundfile_module.write = lambda path, _audio, _sr: write_wav(Path(path))
    torch_module = types.ModuleType("torch")
    torch_module.float16 = "float16"
    torch_module.bfloat16 = "bfloat16"
    torch_module.float32 = "float32"
    torch_module.cuda = types.SimpleNamespace(is_available=lambda: False)
    torch_module.backends = types.SimpleNamespace(
        mps=types.SimpleNamespace(is_available=lambda: False)
    )

    with unittest.mock.patch.dict(
        sys.modules,
        {
            "omnivoice": omnivoice_module,
            "omnivoice.models": models_module,
            "omnivoice.models.omnivoice": model_module,
            "soundfile": soundfile_module,
            "torch": torch_module,
        },
    ):
        yield FakeOmniVoiceModel


class MockStudioHandler(http.server.BaseHTTPRequestHandler):
    requests: list[dict] = []
    profiles_payload: list[dict] = [{"id": "studio-123", "name": "Studio Voice"}]

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        type(self).requests.append({"path": self.path, "method": "GET"})
        if self.path != "/profiles":
            self.send_response(404)
            self.end_headers()
            return
        payload = json.dumps(type(self).profiles_payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        type(self).requests.append(
            {
                "path": self.path,
                "content_type": self.headers.get("Content-Type", ""),
                "body": body,
            }
        )
        if self.path != "/generate":
            self.send_response(404)
            self.end_headers()
            return
        payload = wav_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return None


class ErrorStudioHandler(http.server.BaseHTTPRequestHandler):
    response_body = b""

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(type(self).response_body)))
        self.end_headers()
        self.wfile.write(type(self).response_body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return None


@contextlib.contextmanager
def mock_studio_server():
    MockStudioHandler.requests = []
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MockStudioHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", MockStudioHandler.requests
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


@contextlib.contextmanager
def error_studio_server(response_body: bytes):
    ErrorStudioHandler.response_body = response_body
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ErrorStudioHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


class OmniVoiceRegistryTests(unittest.TestCase):
    def test_loads_valid_clone_voice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)
            voice_dir = write_voice(voices_root)
            profile, resolved_dir = omnivoice.load_voice_profile(voices_root, "marvin")
            validated = omnivoice.validate_voice_profile(profile, resolved_dir)

            self.assertEqual(resolved_dir, voice_dir.resolve())
            self.assertEqual(validated["engine"], "omnivoice")
            self.assertEqual(validated["ref_audio_path"], str((voice_dir / "ref.wav").resolve()))

    def test_missing_voice_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "voice profile not found"):
                omnivoice.load_voice_profile(Path(tmp), "missing")

    def test_dot_segment_voice_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for voice_id in (".", ".."):
                with self.subTest(voice_id=voice_id):
                    with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "voice id"):
                        omnivoice.resolve_voice_dir(Path(tmp), voice_id)

    def test_symlink_voice_dir_escape_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            symlink = root / "voices" / "escape"
            symlink.parent.mkdir()
            try:
                symlink.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")

            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "escapes"):
                omnivoice.resolve_voice_dir(root / "voices", "escape")

    def test_invalid_consent_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)
            write_voice(voices_root, consent_status="pending")
            profile, voice_dir = omnivoice.load_voice_profile(voices_root, "marvin")

            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "consent.status"):
                omnivoice.validate_voice_profile(profile, voice_dir)

    def test_missing_ref_audio_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)
            write_voice(voices_root, ref_audio="missing.wav")
            profile, voice_dir = omnivoice.load_voice_profile(voices_root, "marvin")

            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "ref_audio is missing"):
                omnivoice.validate_voice_profile(profile, voice_dir)

    def test_invalid_ref_audio_wav_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)
            voice_dir = write_voice(voices_root, ref_audio="bad.wav")
            (voice_dir / "bad.wav").write_text("not a wav", encoding="utf-8")
            profile, resolved_dir = omnivoice.load_voice_profile(voices_root, "marvin")

            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "valid WAV"):
                omnivoice.validate_voice_profile(profile, resolved_dir)

    def test_profile_speed_must_be_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            voice_dir = write_voice(voices_root)
            profile_path = voice_dir / "voice.yaml"
            profile_yaml = profile_path.read_text(encoding="utf-8")
            profile_path.write_text(
                profile_yaml.replace("speed: 1.0", "speed: 0"),
                encoding="utf-8",
            )
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["backend"])},
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be greater than 0", stderr.getvalue())

    def test_cli_speed_must_be_finite_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--voice",
                        "marvin",
                        "--speed",
                        "nan",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["backend"])},
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be greater than 0", stderr.getvalue())
            self.assertFalse(out_file.exists())

    def test_timeout_must_be_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--voice",
                        "marvin",
                        "--timeout",
                        "0",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["backend"])},
                )

            self.assertEqual(result, 1)
            self.assertIn("timeout must be greater than 0", stderr.getvalue())
            self.assertFalse(out_file.exists())

    def test_text_file_must_not_exceed_max_chars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("x" * 11, encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--voice",
                        "marvin",
                        "--max-chars",
                        "10",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["backend"])},
                )

            self.assertEqual(result, 1)
            self.assertIn("text file exceeds max text length", stderr.getvalue())
            self.assertFalse(out_file.exists())

    def test_command_failure_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            command = [
                sys.executable,
                "-c",
                "import sys; sys.stderr.write('backend failed'); sys.exit(7)",
            ]

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(root / "out.wav"),
                    "--voice",
                    "marvin",
                ],
                env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
            )

            self.assertEqual(result, 1)

    def test_command_failure_redacts_backend_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            password_key = "PASS" + "WORD"
            token_key = "to" + "ken"
            token_value = "hf" + "_" + ("A" * 24)
            command = [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "sys.stderr.write('backend failed "
                    + password_key
                    + "=topsecret "
                    + token_key
                    + ": lowersecret "
                    + token_value
                    + "'); "
                    "sys.exit(7)"
                ),
            ]
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("backend failed", error)
            self.assertIn(f"{password_key}=[redacted]", error)
            self.assertIn(f"{token_key}: [redacted]", error)
            self.assertIn("hf_[redacted]", error)
            self.assertNotIn("topsecret", error)
            self.assertNotIn("lowersecret", error)
            self.assertNotIn(token_value, error)

    def test_command_json_unknown_placeholder_returns_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={
                        "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                            ["backend", "{missing_placeholder}"]
                        )
                    },
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("HERMES_OMNIVOICE_COMMAND_JSON", error)
            self.assertIn("{missing_placeholder}", error)
            self.assertIn("unknown placeholder", error)
            self.assertNotIn("Traceback", error)

    def test_command_string_unknown_placeholder_returns_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={"HERMES_OMNIVOICE_COMMAND": "backend {missing_placeholder}"},
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("HERMES_OMNIVOICE_COMMAND", error)
            self.assertIn("{missing_placeholder}", error)
            self.assertIn("unknown placeholder", error)
            self.assertNotIn("Traceback", error)

    def test_command_json_invalid_placeholder_syntax_returns_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={
                        "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                            ["backend", "{text_file"]
                        )
                    },
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("HERMES_OMNIVOICE_COMMAND_JSON", error)
            self.assertIn("invalid placeholder syntax", error)
            self.assertNotIn("Traceback", error)

    def test_command_json_unsupported_placeholder_access_returns_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--voice",
                        "marvin",
                    ],
                    env={
                        "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                            ["backend", "{text_file.name}"]
                        )
                    },
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("HERMES_OMNIVOICE_COMMAND_JSON", error)
            self.assertIn("{text_file.name}", error)
            self.assertIn("unsupported placeholder access", error)
            self.assertNotIn("Traceback", error)

    def test_command_success_writes_valid_wav(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            command = [
                sys.executable,
                str(FAKE_BACKEND_PATH),
                "--text-file",
                "{text_file}",
                "--out",
                "{out}",
                "--voice-dir",
                "{voice_dir}",
                "--speed",
                "{speed}",
            ]

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(out_file),
                    "--voice",
                    "marvin",
                ],
                env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
            )

            self.assertEqual(result, 0)
            self.assertEqual(path_mode(out_file), 0o600)
            with wave.open(str(out_file), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertGreater(wav.getnframes(), 0)

    def test_command_backend_replaces_output_symlink_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            target = root / "target.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            target.write_text("sentinel", encoding="utf-8")
            try:
                out_file.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")
            command = [
                sys.executable,
                str(FAKE_BACKEND_PATH),
                "--text-file",
                "{text_file}",
                "--out",
                "{out}",
                "--voice-dir",
                "{voice_dir}",
                "--speed",
                "{speed}",
            ]

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(out_file),
                    "--voice",
                    "marvin",
                ],
                env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
            )

            self.assertEqual(result, 0)
            self.assertFalse(out_file.is_symlink())
            self.assertEqual(target.read_text(encoding="utf-8"), "sentinel")
            self.assertEqual(path_mode(out_file), 0o600)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)

    def test_command_backend_receives_private_temp_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            captured_out = root / "captured-out.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            command = [
                sys.executable,
                "-c",
                (
                    "import sys, wave; "
                    "open(sys.argv[2], 'w', encoding='utf-8').write(sys.argv[1]); "
                    "wav=wave.open(sys.argv[1], 'wb'); "
                    "wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(16000); "
                    "wav.writeframes(b'\\x00\\x00' * 160); wav.close()"
                ),
                "{out}",
                str(captured_out),
            ]

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(out_file),
                    "--voice",
                    "marvin",
                ],
                env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
            )

            self.assertEqual(result, 0)
            backend_out = Path(captured_out.read_text(encoding="utf-8"))
            self.assertNotEqual(backend_out, out_file)
            self.assertEqual(backend_out.parent.resolve(), out_file.parent.resolve())
            self.assertTrue(backend_out.name.startswith(f".{out_file.name}."))
            self.assertFalse(backend_out.exists())
            self.assertEqual(path_mode(out_file), 0o600)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)

    def test_command_backend_invalid_temp_output_does_not_replace_final(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            command = [
                sys.executable,
                "-c",
                "import pathlib, sys; pathlib.Path(sys.argv[1]).write_text('not a wav')",
                "{out}",
            ]

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(out_file),
                    "--voice",
                    "marvin",
                ],
                env={"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
            )

            self.assertEqual(result, 1)
            self.assertFalse(out_file.exists())
            self.assertEqual(list(out_file.parent.glob(f".{out_file.name}.*")), [])

    def test_auto_cli_builds_official_clone_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            profile, voice_dir = omnivoice.load_voice_profile(voices_root, "marvin")
            profile = omnivoice.validate_voice_profile(profile, voice_dir)

            with unittest.mock.patch.object(
                omnivoice.shutil,
                "which",
                return_value="/usr/local/bin/omnivoice-infer",
            ):
                command = omnivoice.build_backend_command(
                    env={
                        "HERMES_OMNIVOICE_AUTO_CLI": "1",
                        "HERMES_OMNIVOICE_MODEL": "k2-fsa/OmniVoice",
                        "HERMES_OMNIVOICE_DEVICE": "mps",
                    },
                    profile=profile,
                    voice_id="marvin",
                    voice_dir=voice_dir,
                    text_file=text_file,
                    text=text_file.read_text(encoding="utf-8"),
                    output_path=root / "out.wav",
                    speed="1.25",
                )

            self.assertEqual(command[0], "/usr/local/bin/omnivoice-infer")
            self.assertIn("--text", command)
            self.assertIn("Hermes custom voice synthesis test.", command)
            self.assertIn("--output", command)
            self.assertIn("--speed", command)
            self.assertIn("1.25", command)
            self.assertIn("--language", command)
            self.assertIn("en", command)
            self.assertIn("--device", command)
            self.assertIn("mps", command)
            self.assertIn("--ref_audio", command)
            self.assertIn(profile["ref_audio_path"], command)
            self.assertIn("--ref_text", command)

    def test_auto_cli_builds_official_design_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "narrator")
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            profile, voice_dir = omnivoice.load_voice_profile(voices_root, "narrator")
            profile = omnivoice.validate_voice_profile(profile, voice_dir)

            with unittest.mock.patch.object(
                omnivoice.shutil,
                "which",
                return_value="/usr/local/bin/omnivoice-infer",
            ):
                command = omnivoice.build_backend_command(
                    env={"HERMES_OMNIVOICE_AUTO_CLI": "1"},
                    profile=profile,
                    voice_id="narrator",
                    voice_dir=voice_dir,
                    text_file=text_file,
                    text=text_file.read_text(encoding="utf-8"),
                    output_path=root / "out.wav",
                    speed="1.0",
                )

            self.assertEqual(command[0], "/usr/local/bin/omnivoice-infer")
            self.assertIn("--model", command)
            self.assertIn("k2-fsa/OmniVoice", command)
            self.assertIn("--instruct", command)
            self.assertIn(profile["instruct"], command)
            self.assertNotIn("--ref_audio", command)

    def test_auto_cli_rejects_empty_model_before_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "narrator")
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            profile, voice_dir = omnivoice.load_voice_profile(voices_root, "narrator")
            profile = omnivoice.validate_voice_profile(profile, voice_dir)

            with unittest.mock.patch.object(
                omnivoice.shutil,
                "which",
                return_value="/usr/local/bin/omnivoice-infer",
            ):
                with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "model must not be empty"):
                    omnivoice.build_backend_command(
                        env={
                            "HERMES_OMNIVOICE_AUTO_CLI": "1",
                            "HERMES_OMNIVOICE_MODEL": " ",
                        },
                        profile=profile,
                        voice_id="narrator",
                        voice_dir=voice_dir,
                        text_file=text_file,
                        text=text_file.read_text(encoding="utf-8"),
                        output_path=root / "out.wav",
                        speed="1.0",
                    )

    def test_design_instruct_rejects_unsupported_english_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)
            voice_dir = voices_root / "bad"
            voice_dir.mkdir(parents=True)
            (voice_dir / "voice.yaml").write_text(
                """id: bad
name: Bad
engine: omnivoice
mode: design
instruct: "calm local assistant, clear delivery"
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
    - local_generation
""",
                encoding="utf-8",
            )
            profile, resolved_dir = omnivoice.load_voice_profile(voices_root, "bad")

            with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "unsupported"):
                omnivoice.validate_voice_profile(profile, resolved_dir)

    def test_studio_url_must_be_loopback_by_default(self) -> None:
        with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "non-loopback"):
            omnivoice.validate_studio_url("http://10.0.0.5:3900", {})

    def test_studio_url_accepts_loopback(self) -> None:
        self.assertEqual(
            omnivoice.validate_studio_url("http://127.0.0.1:3900/", {}),
            "http://127.0.0.1:3900",
        )

    def test_studio_url_rejects_userinfo(self) -> None:
        with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "userinfo"):
            omnivoice.validate_studio_url("http://user:cred@127.0.0.1:3900", {})

    def test_studio_url_allows_remote_with_explicit_override(self) -> None:
        self.assertEqual(
            omnivoice.validate_studio_url(
                "http://10.0.0.5:3900",
                {"HERMES_OMNIVOICE_ALLOW_REMOTE_STUDIO": "1"},
            ),
            "http://10.0.0.5:3900",
        )

    def test_studio_api_success_writes_valid_wav_and_sends_profile_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "narrator", studio_profile_id="studio-123")
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")

            with mock_studio_server() as (studio_url, requests):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--voice",
                        "narrator",
                    ],
                    env={"HERMES_OMNIVOICE_STUDIO_URL": studio_url},
                )

            self.assertEqual(result, 0)
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0]["path"], "/generate")
            self.assertIn("multipart/form-data", requests[0]["content_type"])
            self.assertIn(b'name="profile_id"', requests[0]["body"])
            self.assertIn(b"studio-123", requests[0]["body"])
            self.assertIn(b"Hermes custom voice synthesis test.", requests[0]["body"])
            self.assertEqual(path_mode(out_file), 0o600)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)

    def test_studio_api_http_error_redacts_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "narrator", studio_profile_id="studio-123")
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            key_name = "api" + "_key"
            token_value = "hf" + "_" + ("B" * 24)
            body = (
                "generation failed "
                + key_name
                + ": studiosecret "
                + token_value
            ).encode("utf-8")
            stderr = io.StringIO()

            with error_studio_server(body) as studio_url:
                with contextlib.redirect_stderr(stderr):
                    result = omnivoice.run(
                        [
                            "--voices-dir",
                            str(voices_root),
                            "--text-file",
                            str(text_file),
                            "--out",
                            str(out_file),
                            "--voice",
                            "narrator",
                        ],
                        env={"HERMES_OMNIVOICE_STUDIO_URL": studio_url},
                    )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("OmniVoice-Studio API failed with HTTP 500", error)
            self.assertIn(f"{key_name}: [redacted]", error)
            self.assertIn("hf_[redacted]", error)
            self.assertNotIn("studiosecret", error)
            self.assertNotIn(token_value, error)

    def test_studio_api_replaces_output_symlink_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "narrator", studio_profile_id="studio-123")
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            target = root / "target.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            target.write_text("sentinel", encoding="utf-8")
            try:
                out_file.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")

            with mock_studio_server() as (studio_url, _requests):
                result = omnivoice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--voice",
                        "narrator",
                    ],
                    env={"HERMES_OMNIVOICE_STUDIO_URL": studio_url},
                )

            self.assertEqual(result, 0)
            self.assertFalse(out_file.is_symlink())
            self.assertEqual(target.read_text(encoding="utf-8"), "sentinel")
            self.assertEqual(path_mode(out_file), 0o600)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)


class OmniVoiceIntegrationTests(unittest.TestCase):
    def test_real_omnivoice_backend_is_configured(self) -> None:
        if os.environ.get("HERMES_OMNIVOICE_RUN_REAL_TEST") != "1":
            self.skipTest("set HERMES_OMNIVOICE_RUN_REAL_TEST=1 to run real synthesis")

        runtime_env = {
            key: os.environ[key]
            for key in (
                "HERMES_OMNIVOICE_COMMAND_JSON",
                "HERMES_OMNIVOICE_COMMAND",
                "HERMES_OMNIVOICE_STUDIO_URL",
                "HERMES_OMNIVOICE_AUTO_CLI",
                "HERMES_OMNIVOICE_MODEL",
                "HERMES_OMNIVOICE_DEVICE",
                "HERMES_OMNIVOICE_DTYPE",
            )
            if key in os.environ
        }
        self.assertTrue(
            any(
                runtime_env.get(key)
                for key in (
                    "HERMES_OMNIVOICE_COMMAND_JSON",
                    "HERMES_OMNIVOICE_COMMAND",
                    "HERMES_OMNIVOICE_STUDIO_URL",
                    "HERMES_OMNIVOICE_AUTO_CLI",
                )
            ),
            "set a real OmniVoice backend env var before enabling the integration test",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_design_voice(voices_root, "real")
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")

            result = omnivoice.run(
                [
                    "--voices-dir",
                    str(voices_root),
                    "--text-file",
                    str(text_file),
                    "--out",
                    str(out_file),
                    "--voice",
                    "real",
                ],
                env=runtime_env,
            )

            self.assertEqual(result, 0)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)


class PythonAdapterTests(unittest.TestCase):
    def test_python_adapter_generates_clone_audio_with_fake_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            ref_audio = root / "ref.wav"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            write_wav(ref_audio)

            with fake_omnivoice_python_modules() as fake_model:
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--ref-audio",
                        str(ref_audio),
                        "--ref-text",
                        "Reference transcript.",
                        "--language",
                        "en",
                        "--speed",
                        "1.2",
                        "--model",
                        "local-model",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(fake_model.captured_load["model"], "local-model")
            self.assertEqual(fake_model.captured_load["device_map"], "cpu")
            self.assertEqual(fake_model.captured_load["dtype"], "float16")
            self.assertEqual(
                fake_model.captured_generate["text"],
                "Hermes custom voice synthesis test.",
            )
            self.assertEqual(fake_model.captured_generate["ref_audio"], str(ref_audio.resolve()))
            self.assertEqual(fake_model.captured_generate["ref_text"], "Reference transcript.")
            self.assertEqual(fake_model.captured_generate["language"], "en")
            self.assertEqual(fake_model.captured_generate["speed"], 1.2)
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)

    def test_python_adapter_generates_design_audio_with_fake_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            out_file = root / "out.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")

            with fake_omnivoice_python_modules() as fake_model:
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(out_file),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--device",
                        "mps",
                        "--dtype",
                        "float32",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(fake_model.captured_load["device_map"], "mps")
            self.assertEqual(fake_model.captured_load["dtype"], "float32")
            self.assertEqual(
                fake_model.captured_generate["instruct"],
                "male, american accent, moderate pitch",
            )
            self.assertNotIn("ref_audio", fake_model.captured_generate)

    def test_python_adapter_requires_clone_text_when_ref_audio_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            ref_audio = root / "ref.wav"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            write_wav(ref_audio)

            with fake_omnivoice_python_modules():
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--ref-audio",
                        str(ref_audio),
                    ]
                )

            self.assertEqual(result, 1)

    def test_python_adapter_rejects_invalid_speed_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--speed",
                        "nan",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be a finite number greater than 0", stderr.getvalue())
            load_backend.assert_not_called()

    def test_python_adapter_rejects_non_positive_speed_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--speed",
                        "0",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be a finite number greater than 0", stderr.getvalue())
            load_backend.assert_not_called()

    def test_python_adapter_rejects_sample_rate_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--sample-rate",
                        "0",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("sample rate must be greater than 0", stderr.getvalue())
            load_backend.assert_not_called()

    def test_python_adapter_rejects_backend_zero_sample_rate_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with fake_omnivoice_python_modules() as fake_model, contextlib.redirect_stderr(stderr):
                fake_model.sampling_rate = 0
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("sample rate must be greater than 0", stderr.getvalue())

    def test_python_adapter_rejects_backend_non_integer_sample_rate_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with fake_omnivoice_python_modules() as fake_model, contextlib.redirect_stderr(stderr):
                fake_model.sampling_rate = "not-a-rate"
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("sample rate must be an integer greater than 0", stderr.getvalue())

    def test_python_adapter_rejects_empty_model_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--model",
                        " ",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("model must not be empty", stderr.getvalue())
            load_backend.assert_not_called()

    def test_python_adapter_rejects_empty_device_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--device",
                        " ",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("device must not be empty", stderr.getvalue())
            load_backend.assert_not_called()

    def test_python_adapter_rejects_empty_dtype_before_backend_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text_file = root / "input.txt"
            text_file.write_text("Hermes custom voice synthesis test.", encoding="utf-8")
            stderr = io.StringIO()

            with unittest.mock.patch.object(python_adapter, "_load_backend") as load_backend, \
                contextlib.redirect_stderr(stderr):
                result = python_adapter.run(
                    [
                        "--text-file",
                        str(text_file),
                        "--out",
                        str(root / "out.wav"),
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--dtype",
                        " ",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("dtype must not be empty", stderr.getvalue())
            load_backend.assert_not_called()


class PythonEnvSetupTests(unittest.TestCase):
    def test_setup_env_dry_run_plans_command_json_without_creating_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp) / "omnivoice-env"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(venv_dir),
                        "--dry-run",
                        "--json",
                    ]
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["status"], "planned")
            self.assertFalse(venv_dir.exists())
            self.assertEqual(report["package"], "omnivoice")
            self.assertTrue(report["setup_python_supported"])
            self.assertIn("HERMES_OMNIVOICE_COMMAND_JSON", report["env"])
            command = json.loads(report["env"]["HERMES_OMNIVOICE_COMMAND_JSON"])
            self.assertEqual(command[0], str(setup_env.venv_python(venv_dir.resolve())))
            self.assertTrue(command[1].endswith("hermes-omnivoice-python-adapter.py"))
            self.assertIn("{ref_audio}", command)
            self.assertIn("{instruct}", command)

    def test_setup_env_shell_prints_exportable_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp) / "omnivoice-env"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(venv_dir),
                        "--dry-run",
                        "--shell",
                    ]
                )

            exports: dict[str, str] = {}
            for line in output.getvalue().strip().splitlines():
                self.assertTrue(line.startswith("export "))
                assignment = shlex.split(line.removeprefix("export "))[0]
                key, value = assignment.split("=", 1)
                exports[key] = value

            self.assertEqual(result, 0)
            self.assertEqual(exports["HERMES_OMNIVOICE_MODEL"], "k2-fsa/OmniVoice")
            command = json.loads(exports["HERMES_OMNIVOICE_COMMAND_JSON"])
            self.assertEqual(command[0], str(setup_env.venv_python(venv_dir.resolve())))
            self.assertTrue(command[1].endswith("hermes-omnivoice-python-adapter.py"))

    def test_setup_env_rejects_empty_model_before_plan(self) -> None:
        errors = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(errors):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(Path(tmp) / "omnivoice-env"),
                        "--model",
                        " ",
                        "--dry-run",
                    ]
                )

        self.assertEqual(result, 1)
        self.assertIn("model must not be empty", errors.getvalue())

    def test_setup_env_rejects_empty_package_before_plan(self) -> None:
        errors = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(errors):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(Path(tmp) / "omnivoice-env"),
                        "--package",
                        " ",
                        "--dry-run",
                    ]
                )

        self.assertEqual(result, 1)
        self.assertIn("package must not be empty", errors.getvalue())

    def test_setup_env_prefers_supported_python_candidate(self) -> None:
        def fake_which(name: str) -> str | None:
            return {
                "python3.11": "/opt/test/bin/python3.11",
                "python3": "/opt/test/bin/python3.14",
            }.get(name)

        def fake_version(path: str) -> tuple[int, int, int]:
            if path.endswith("python3.11"):
                return 3, 11, 9
            return 3, 14, 4

        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with unittest.mock.patch.object(setup_env.shutil, "which", side_effect=fake_which):
                with unittest.mock.patch.object(
                    setup_env,
                    "detect_python_version",
                    side_effect=fake_version,
                ):
                    with contextlib.redirect_stdout(output):
                        result = setup_env.run(
                            [
                                "--venv-dir",
                                str(Path(tmp) / "omnivoice-env"),
                                "--dry-run",
                                "--json",
                            ]
                        )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["setup_python"], "/opt/test/bin/python3.11")
            self.assertEqual(report["setup_python_version"], "3.11.9")

    def test_setup_env_rejects_unsupported_python_without_override(self) -> None:
        errors = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.object(
                setup_env,
                "detect_python_version",
                return_value=(3, 14, 4),
            ):
                with contextlib.redirect_stderr(errors):
                    result = setup_env.run(
                        [
                            "--venv-dir",
                            str(Path(tmp) / "omnivoice-env"),
                            "--python",
                            "/opt/test/bin/python3.14",
                            "--dry-run",
                        ]
                    )

        self.assertEqual(result, 1)
        self.assertIn("outside the supported setup range", errors.getvalue())

    def test_setup_env_check_only_reports_missing_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(Path(tmp) / "missing"),
                        "--check-only",
                        "--json",
                    ]
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["status"], "checked")
            self.assertFalse(report["ready"])
            self.assertFalse(report["python_exists"])

    def test_setup_env_require_ready_fails_for_missing_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                result = setup_env.run(
                    [
                        "--venv-dir",
                        str(Path(tmp) / "missing"),
                        "--check-only",
                        "--require-ready",
                    ]
                )

            self.assertEqual(result, 1)


class StudioImportTests(unittest.TestCase):
    def test_import_requires_explicit_consent_before_network(self) -> None:
        result = studio_import.run(
            [
                "--studio-url",
                "http://127.0.0.1:3900",
                "--profile-id",
                "marvin",
            ]
        )

        self.assertEqual(result, 1)

    def test_importer_refuses_remote_studio_by_default(self) -> None:
        with self.assertRaisesRegex(studio_import.ImportErrorWithContext, "non-loopback"):
            studio_import.validate_studio_url("http://10.0.0.5:3900")

    def test_importer_rejects_studio_url_userinfo(self) -> None:
        with self.assertRaisesRegex(studio_import.ImportErrorWithContext, "userinfo"):
            studio_import.validate_studio_url("http://user:cred@127.0.0.1:3900")

    def test_importer_rejects_dot_segment_voice_id_before_network(self) -> None:
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            result = studio_import.run(
                [
                    "--studio-url",
                    "http://127.0.0.1:3900",
                    "--profile-id",
                    "studio-123",
                    "--voice-id",
                    "..",
                    "--confirm-consent",
                ]
            )

        self.assertEqual(result, 1)
        self.assertIn("voice id contains unsupported characters", errors.getvalue())

    def test_importer_rejects_symlink_voice_dir_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            symlink = root / "voices" / "escape"
            symlink.parent.mkdir()
            try:
                symlink.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")

            with self.assertRaisesRegex(studio_import.ImportErrorWithContext, "escapes"):
                studio_import.resolve_voice_dir(root / "voices", "escape")

    def test_importer_rejects_existing_voice_without_force_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voice_dir = root / "voices" / "marvin"
            voice_dir.mkdir(parents=True)
            (voice_dir / "voice.yaml").write_text("id: marvin\n", encoding="utf-8")
            errors = io.StringIO()

            with contextlib.redirect_stderr(errors):
                result = studio_import.run(
                    [
                        "--studio-url",
                        "http://127.0.0.1:3900",
                        "--profile-id",
                        "studio-123",
                        "--voice-id",
                        "marvin",
                        "--voices-dir",
                        str(root / "voices"),
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("already contains files", errors.getvalue())

    def test_importer_rejects_empty_allowed_use_before_network(self) -> None:
        with unittest.mock.patch.object(studio_import, "request_json") as request_json:
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                result = studio_import.run(
                    [
                        "--studio-url",
                        "http://127.0.0.1:3900",
                        "--profile-id",
                        "studio-123",
                        "--allowed-use",
                        "  ",
                        "--confirm-consent",
                    ]
                )

        self.assertEqual(result, 1)
        self.assertIn("allowed uses cannot be empty", errors.getvalue())
        request_json.assert_not_called()

    def test_importer_rejects_invalid_timeout_before_network_and_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_dir = Path(tmp) / "voices"
            with unittest.mock.patch.object(studio_import, "request_json") as request_json:
                errors = io.StringIO()
                with contextlib.redirect_stderr(errors):
                    result = studio_import.run(
                        [
                            "--studio-url",
                            "http://127.0.0.1:3900",
                            "--profile-id",
                            "studio-123",
                            "--voice-id",
                            "marvin",
                            "--voices-dir",
                            str(voices_dir),
                            "--timeout",
                            "0",
                            "--confirm-consent",
                        ]
                    )

            self.assertEqual(result, 1)
            self.assertIn("timeout must be greater than 0", errors.getvalue())
            request_json.assert_not_called()
            self.assertFalse((voices_dir / "marvin").exists())

    def test_importer_rejects_invalid_downloaded_wav(self) -> None:
        with self.assertRaisesRegex(studio_import.ImportErrorWithContext, "valid WAV"):
            studio_import.validate_wav_bytes(b"not a wav")

    def test_importer_writes_registry_yaml_compatible_with_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voice_dir = root / "marvin"
            voice_dir.mkdir()
            write_wav(voice_dir / "ref.wav")
            profile = {
                "id": "studio-123",
                "name": "Marvin",
                "ref_text": "Reference transcript.",
                "instruct": "clear local assistant voice",
                "language": "en",
            }

            studio_import.write_voice_yaml(
                voice_dir / "voice.yaml",
                profile,
                "marvin",
                "clone",
                ["personal_assistant", "local_generation"],
            )
            loaded, resolved_dir = omnivoice.load_voice_profile(root, "marvin")
            validated = omnivoice.validate_voice_profile(loaded, resolved_dir)

            self.assertEqual(validated["studio_profile_id"], "studio-123")
            self.assertEqual(validated["consent"]["status"], "confirmed")
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)

    def test_importer_quotes_allowed_uses_in_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voice_dir = root / "narrator"
            voice_dir.mkdir()
            profile = {
                "id": "studio-123",
                "name": "Narrator",
                "instruct": "male, american accent, moderate pitch",
                "language": "en",
            }

            studio_import.write_voice_yaml(
                voice_dir / "voice.yaml",
                profile,
                "narrator",
                "design",
                ["local: generation", "review # internal"],
            )
            loaded, resolved_dir = omnivoice.load_voice_profile(root, "narrator")
            validated = omnivoice.validate_voice_profile(loaded, resolved_dir)

            self.assertEqual(
                validated["consent"]["allowed_uses"],
                ["local: generation", "review # internal"],
            )
            yaml_text = (voice_dir / "voice.yaml").read_text(encoding="utf-8")
            self.assertIn('    - "local: generation"', yaml_text)
            self.assertIn('    - "review # internal"', yaml_text)

    def test_importer_writes_private_profile_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            profile = {
                "id": "studio-123",
                "name": "Marvin",
                "ref_text": "Reference transcript.",
                "language": "en",
            }

            with unittest.mock.patch.object(studio_import, "request_json", return_value=profile):
                with unittest.mock.patch.object(studio_import, "request_bytes", return_value=wav_bytes()):
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = studio_import.run(
                            [
                                "--studio-url",
                                "http://127.0.0.1:3900",
                                "--profile-id",
                                "studio-123",
                                "--voice-id",
                                "marvin",
                                "--voices-dir",
                                str(voices_root),
                                "--confirm-consent",
                            ]
                        )

            voice_dir = voices_root / "marvin"
            self.assertEqual(result, 0)
            self.assertEqual(path_mode(voice_dir), 0o700)
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)
            self.assertEqual(path_mode(voice_dir / "ref.wav"), 0o600)

    def test_importer_force_replaces_existing_material_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            voice_dir = voices_root / "marvin"
            voice_dir.mkdir(parents=True)
            yaml_target = root / "outside.yaml"
            audio_target = root / "outside.wav"
            yaml_target.write_text("sentinel-yaml", encoding="utf-8")
            audio_target.write_text("sentinel-audio", encoding="utf-8")
            try:
                (voice_dir / "voice.yaml").symlink_to(yaml_target)
                (voice_dir / "ref.wav").symlink_to(audio_target)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")
            profile = {
                "id": "studio-123",
                "name": "Marvin",
                "ref_text": "Reference transcript.",
                "language": "en",
            }

            with unittest.mock.patch.object(studio_import, "request_json", return_value=profile):
                with unittest.mock.patch.object(studio_import, "request_bytes", return_value=wav_bytes()):
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = studio_import.run(
                            [
                                "--studio-url",
                                "http://127.0.0.1:3900",
                                "--profile-id",
                                "studio-123",
                                "--voice-id",
                                "marvin",
                                "--voices-dir",
                                str(voices_root),
                                "--confirm-consent",
                                "--force",
                            ]
                        )

            self.assertEqual(result, 0)
            self.assertFalse((voice_dir / "voice.yaml").is_symlink())
            self.assertFalse((voice_dir / "ref.wav").is_symlink())
            self.assertEqual(yaml_target.read_text(encoding="utf-8"), "sentinel-yaml")
            self.assertEqual(audio_target.read_text(encoding="utf-8"), "sentinel-audio")
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)
            self.assertEqual(path_mode(voice_dir / "ref.wav"), 0o600)


class CreateVoiceTests(unittest.TestCase):
    def test_create_design_voice_validates_with_confirmed_consent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp)

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "design",
                        "narrator",
                        "--name",
                        "Narrator",
                        "--instruct",
                        "male, american accent, moderate pitch",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 0)
            loaded, voice_dir = omnivoice.load_voice_profile(voices_root, "narrator")
            validated = omnivoice.validate_voice_profile(loaded, voice_dir)
            self.assertEqual(validated["mode"], "design")
            self.assertEqual(validated["consent"]["source"], "user_created")
            self.assertEqual(path_mode(voice_dir), 0o700)
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)

    def test_create_design_voice_rejects_invalid_speed_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp) / "voices"
            stderr = io.StringIO()

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "design",
                        "narrator",
                        "--instruct",
                        "calm voice",
                        "--speed",
                        "nan",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be greater than 0", stderr.getvalue())
            self.assertFalse((voices_root / "narrator").exists())

    def test_create_design_voice_rejects_empty_allowed_use_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_root = Path(tmp) / "voices"
            stderr = io.StringIO()

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "design",
                        "narrator",
                        "--instruct",
                        "calm voice",
                        "--allowed-use",
                        "   ",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("allowed uses cannot be empty", stderr.getvalue())
            self.assertFalse((voices_root / "narrator").exists())

    def test_create_clone_voice_requires_confirmed_consent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref_audio = root / "ref.wav"
            write_wav(ref_audio)

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(root / "voices"),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(ref_audio),
                        "--ref-text",
                        "Reference transcript.",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertFalse((root / "voices" / "marvin" / "voice.yaml").exists())

    def test_create_clone_voice_rejects_invalid_wav(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_ref = root / "bad.wav"
            bad_ref.write_text("not a wav", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(root / "voices"),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(bad_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertFalse((root / "voices" / "marvin" / "voice.yaml").exists())

    def test_create_clone_voice_copies_wav_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            source_ref = root / "source.wav"
            write_wav(source_ref)

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "clone",
                        "marvin",
                        "--name",
                        "Marvin",
                        "--ref-audio",
                        str(source_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertTrue((voices_root / "marvin" / "ref.wav").is_file())
            loaded, voice_dir = omnivoice.load_voice_profile(voices_root, "marvin")
            validated = omnivoice.validate_voice_profile(loaded, voice_dir)
            self.assertEqual(validated["mode"], "clone")
            self.assertEqual(
                validated["ref_audio_path"],
                str((voices_root / "marvin" / "ref.wav").resolve()),
            )

    def test_create_clone_voice_writes_private_profile_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            source_ref = root / "source.wav"
            write_wav(source_ref)

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(source_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--confirm-consent",
                    ]
                )

            voice_dir = voices_root / "marvin"
            self.assertEqual(result, 0)
            self.assertEqual(path_mode(voice_dir), 0o700)
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)
            self.assertEqual(path_mode(voice_dir / "ref.wav"), 0o600)

    def test_create_clone_voice_rejects_invalid_speed_before_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            source_ref = root / "source.wav"
            write_wav(source_ref)
            stderr = io.StringIO()

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(source_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--speed",
                        "inf",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("speed must be greater than 0", stderr.getvalue())
            self.assertFalse((voices_root / "marvin" / "ref.wav").exists())

    def test_create_clone_voice_rejects_empty_allowed_use_before_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            source_ref = root / "source.wav"
            write_wav(source_ref)
            stderr = io.StringIO()

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(source_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--allowed-use",
                        "   ",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("allowed uses cannot be empty", stderr.getvalue())
            self.assertFalse((voices_root / "marvin" / "ref.wav").exists())

    def test_create_clone_force_replaces_existing_material_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            voice_dir = voices_root / "marvin"
            voice_dir.mkdir(parents=True)
            source_ref = root / "source.wav"
            yaml_target = root / "outside.yaml"
            audio_target = root / "outside.wav"
            write_wav(source_ref)
            yaml_target.write_text("sentinel-yaml", encoding="utf-8")
            audio_target.write_text("sentinel-audio", encoding="utf-8")
            try:
                (voice_dir / "voice.yaml").symlink_to(yaml_target)
                (voice_dir / "ref.wav").symlink_to(audio_target)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "clone",
                        "marvin",
                        "--ref-audio",
                        str(source_ref),
                        "--ref-text",
                        "Reference transcript.",
                        "--confirm-consent",
                        "--force",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertFalse((voice_dir / "voice.yaml").is_symlink())
            self.assertFalse((voice_dir / "ref.wav").is_symlink())
            self.assertEqual(yaml_target.read_text(encoding="utf-8"), "sentinel-yaml")
            self.assertEqual(audio_target.read_text(encoding="utf-8"), "sentinel-audio")
            self.assertEqual(path_mode(voice_dir / "voice.yaml"), 0o600)
            self.assertEqual(path_mode(voice_dir / "ref.wav"), 0o600)

    def test_create_voice_refuses_dot_segment_voice_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        tmp,
                        "design",
                        "..",
                        "--instruct",
                        "calm voice",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)

    def test_create_voice_refuses_existing_directory_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "voices" / "narrator"
            existing.mkdir(parents=True)
            (existing / "voice.yaml").write_text("id: narrator\n", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(root / "voices"),
                        "design",
                        "narrator",
                        "--instruct",
                        "calm voice",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)

    def test_create_voice_rejects_symlink_voice_dir_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            symlink = root / "voices" / "escape"
            symlink.parent.mkdir()
            try:
                symlink.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink setup unavailable: {exc}")

            with contextlib.redirect_stdout(io.StringIO()):
                result = create_voice.run(
                    [
                        "--voices-dir",
                        str(root / "voices"),
                        "design",
                        "escape",
                        "--instruct",
                        "calm voice",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 1)


class RuntimeCheckTests(unittest.TestCase):
    def test_runtime_check_placeholders_match_wrapper_contract(self) -> None:
        self.assertEqual(runtime_check.COMMAND_PLACEHOLDERS, omnivoice.COMMAND_PLACEHOLDERS)

    def test_runtime_check_reports_missing_backend_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = runtime_check.run(
                    ["--voices-dir", str(Path(tmp) / "missing"), "--json"],
                    env={},
                )

            self.assertEqual(result, 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["studio"]["status"], "missing")
            self.assertEqual(report["backend_command"]["status"], "missing")
            self.assertEqual(report["voices_dir"]["status"], "missing")

    def test_runtime_check_refuses_invalid_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = runtime_check.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--timeout",
                        "0",
                        "--json",
                    ],
                    env={},
                )

            self.assertEqual(result, 1)
            self.assertIn("timeout must be greater than 0", stderr.getvalue())

    def test_runtime_check_redacts_backend_command_arguments(self) -> None:
        report = runtime_check.check_backend_command(
            {"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["/bin/echo", "secret-arg"])}
        )

        encoded = json.dumps(report)
        self.assertEqual(report["status"], "configured")
        self.assertEqual(report["mode"], "command_json")
        self.assertIn("echo", report["executable"])
        self.assertNotIn("secret-arg", encoded)

    def test_runtime_check_rejects_command_json_unknown_placeholder(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "unknown placeholder"):
            runtime_check.check_backend_command(
                {
                    "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                        ["/bin/echo", "{missing_placeholder}"]
                    )
                }
            )

    def test_runtime_check_rejects_command_json_invalid_placeholder_syntax(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "invalid placeholder"):
            runtime_check.check_backend_command(
                {"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["/bin/echo", "{text_file"])}
            )

    def test_runtime_check_rejects_command_string_unsupported_placeholder_access(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "unsupported placeholder"):
            runtime_check.check_backend_command(
                {"HERMES_OMNIVOICE_COMMAND": "/bin/echo {text_file.name}"}
            )

    def test_runtime_check_rejects_remote_studio_by_default(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "non-loopback"):
            runtime_check.validate_studio_url("http://10.0.0.5:3900")

    def test_runtime_check_rejects_studio_url_userinfo(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "userinfo"):
            runtime_check.validate_studio_url("http://user:cred@127.0.0.1:3900")

    def test_runtime_check_accepts_loopback_studio_profiles(self) -> None:
        with mock_studio_server() as (studio_url, requests):
            report = runtime_check.check_studio(studio_url, 5, False)

        self.assertEqual(report["status"], "reachable")
        self.assertEqual(report["profile_count"], 1)
        self.assertEqual(requests[0]["path"], "/profiles")

    def test_runtime_check_reports_official_cli_auto_gate(self) -> None:
        with unittest.mock.patch.object(
            runtime_check.shutil,
            "which",
            return_value="/usr/local/bin/omnivoice-infer",
        ):
            report = runtime_check.check_omnivoice_cli(
                {
                    "HERMES_OMNIVOICE_AUTO_CLI": "1",
                    "HERMES_OMNIVOICE_MODEL": "local-model",
                }
            )

        self.assertEqual(report["status"], "found")
        self.assertEqual(report["executable"], "omnivoice-infer")
        self.assertTrue(report["auto_enabled"])
        self.assertEqual(report["model"], "local-model")


class StudioLocalTests(unittest.TestCase):
    def test_loopback_compose_ports_validate(self) -> None:
        config = {
            "services": {
                "omnivoice": {
                    "ports": [
                        {
                            "host_ip": "127.0.0.1",
                            "target": 3900,
                            "published": "3900",
                        }
                    ]
                }
            }
        }

        studio_local.validate_loopback_ports(config, "cpu", 3900)

    def test_broad_compose_ports_fail(self) -> None:
        config = {
            "services": {
                "omnivoice": {
                    "ports": [
                        {
                            "host_ip": "0.0.0.0",
                            "target": 3900,
                            "published": "3900",
                        }
                    ]
                }
            }
        }

        with self.assertRaisesRegex(studio_local.StudioLocalError, "not loopback"):
            studio_local.validate_loopback_ports(config, "cpu", 3900)

    def test_wrong_published_port_fails(self) -> None:
        config = {
            "services": {
                "omnivoice": {
                    "ports": [
                        {
                            "host_ip": "127.0.0.1",
                            "target": 3900,
                            "published": "3901",
                        }
                    ]
                }
            }
        }

        with self.assertRaisesRegex(studio_local.StudioLocalError, "published port"):
            studio_local.validate_loopback_ports(config, "cpu", 3900)

    def test_port_must_be_positive_before_subcommand(self) -> None:
        stderr = io.StringIO()
        with unittest.mock.patch.object(studio_local, "command_check") as command_check, \
            contextlib.redirect_stderr(stderr):
            result = studio_local.run(["check", "--port", "0", "--json"])

        self.assertEqual(result, 1)
        self.assertIn("port must be between 1 and 65535", stderr.getvalue())
        command_check.assert_not_called()

    def test_port_must_not_exceed_tcp_range_before_subcommand(self) -> None:
        stderr = io.StringIO()
        with unittest.mock.patch.object(studio_local, "command_start") as command_start, \
            contextlib.redirect_stderr(stderr):
            result = studio_local.run(["start", "--port", "65536", "--no-fetch"])

        self.assertEqual(result, 1)
        self.assertIn("port must be between 1 and 65535", stderr.getvalue())
        command_start.assert_not_called()

    def test_start_args_can_be_local_only(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.no_build = True
        args.pull = "never"

        with unittest.mock.patch.object(
            studio_local,
            "compose_file",
            return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
        ):
            command = studio_local.compose_up_args(args)

        self.assertIn("--no-build", command)
        self.assertIn("--pull", command)
        self.assertIn("never", command)

    def test_start_no_fetch_does_not_require_git(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.fetch = False
        args.repo_url = "https://example.invalid/repo.git"
        args.update = False
        args.port = 3900
        args.command_timeout = 10
        args.no_build = False
        args.pull = "missing"
        args.cleanup_on_fail = True
        args.remove_volumes_on_fail = False
        args.studio_url = "http://127.0.0.1:3900"
        required: list[str] = []

        def fake_require_binary(name: str) -> str:
            required.append(name)
            if name == "git":
                raise studio_local.StudioLocalError("git should not be required")
            return f"/usr/bin/{name}"

        with unittest.mock.patch.object(studio_local, "require_binary", fake_require_binary), \
            unittest.mock.patch.object(
                studio_local,
                "compose_file",
                return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
            ), unittest.mock.patch.object(
                studio_local,
                "compose_config",
                return_value={
                    "services": {
                        "omnivoice": {
                            "ports": [
                                {
                                    "host_ip": "127.0.0.1",
                                    "target": 3900,
                                    "published": "3900",
                                }
                            ],
                        }
                    }
                },
            ), unittest.mock.patch.object(studio_local, "run_command", return_value=""):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = studio_local.command_start(args)

        self.assertEqual(result, 0)
        self.assertEqual(required, ["docker"])

    def test_no_pull_no_build_start_requires_local_image_before_compose_up(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.fetch = False
        args.port = 3900
        args.command_timeout = 10
        args.no_build = True
        args.pull = "never"
        config = {
            "services": {
                "omnivoice": {
                    "image": "ghcr.io/debpalash/omnivoice-studio:latest",
                    "ports": [
                        {
                            "host_ip": "127.0.0.1",
                            "target": 3900,
                            "published": "3900",
                        }
                    ],
                }
            }
        }

        with unittest.mock.patch.object(studio_local, "require_binary", return_value="/usr/bin/docker"), \
            unittest.mock.patch.object(
                studio_local,
                "compose_file",
                return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
            ), unittest.mock.patch.object(
                studio_local,
                "compose_config",
                return_value=config,
            ), unittest.mock.patch.object(
                studio_local,
                "local_image_exists",
                return_value=False,
            ), unittest.mock.patch.object(studio_local, "run_command") as run_command:
                with self.assertRaisesRegex(studio_local.StudioLocalError, "not available locally"):
                    studio_local.command_start(args)

        run_command.assert_not_called()

    def test_no_build_pull_missing_pulls_image_before_compose_up(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.fetch = False
        args.port = 3900
        args.command_timeout = 10
        args.no_build = True
        args.pull = "missing"
        args.cleanup_on_fail = True
        args.remove_volumes_on_fail = False
        args.studio_url = "http://127.0.0.1:3900"
        config = {
            "services": {
                "omnivoice": {
                    "image": "ghcr.io/debpalash/omnivoice-studio:latest",
                    "ports": [
                        {
                            "host_ip": "127.0.0.1",
                            "target": 3900,
                            "published": "3900",
                        }
                    ],
                }
            }
        }
        commands: list[list[str]] = []

        def fake_run_command(command: list[str], **_kwargs) -> str:
            commands.append(command)
            return ""

        with unittest.mock.patch.object(studio_local, "require_binary", return_value="/usr/bin/docker"), \
            unittest.mock.patch.object(
                studio_local,
                "compose_file",
                return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
            ), unittest.mock.patch.object(
                studio_local,
                "compose_config",
                return_value=config,
            ), unittest.mock.patch.object(
                studio_local,
                "local_image_exists",
                return_value=False,
            ), unittest.mock.patch.object(studio_local, "run_command", fake_run_command):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = studio_local.command_start(args)

        self.assertEqual(result, 0)
        self.assertEqual(
            commands[0],
            ["docker", "pull", "ghcr.io/debpalash/omnivoice-studio:latest"],
        )
        self.assertIn("compose", commands[1])

    def test_no_build_pull_missing_skips_pull_when_local_image_exists(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.fetch = False
        args.port = 3900
        args.command_timeout = 10
        args.no_build = True
        args.pull = "missing"
        args.cleanup_on_fail = True
        args.remove_volumes_on_fail = False
        args.studio_url = "http://127.0.0.1:3900"
        config = {
            "services": {
                "omnivoice": {
                    "image": "ghcr.io/debpalash/omnivoice-studio:latest",
                    "ports": [
                        {
                            "host_ip": "127.0.0.1",
                            "target": 3900,
                            "published": "3900",
                        }
                    ],
                }
            }
        }
        commands: list[list[str]] = []

        def fake_run_command(command: list[str], **_kwargs) -> str:
            commands.append(command)
            return ""

        with unittest.mock.patch.object(studio_local, "require_binary", return_value="/usr/bin/docker"), \
            unittest.mock.patch.object(
                studio_local,
                "compose_file",
                return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
            ), unittest.mock.patch.object(
                studio_local,
                "compose_config",
                return_value=config,
            ), unittest.mock.patch.object(
                studio_local,
                "local_image_exists",
                return_value=True,
            ), unittest.mock.patch.object(studio_local, "run_command", fake_run_command):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = studio_local.command_start(args)

        self.assertEqual(result, 0)
        self.assertEqual(len(commands), 1)
        self.assertIn("compose", commands[0])

    def test_run_command_timeout_fails_cleanly(self) -> None:
        with self.assertRaisesRegex(studio_local.StudioLocalError, "timed out"):
            studio_local.run_command(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                timeout=1,
            )

    def test_command_timeout_zero_remains_unbounded(self) -> None:
        completed = subprocess.CompletedProcess(["true"], 0, "", "")
        with unittest.mock.patch.object(
            studio_local.subprocess,
            "run",
            return_value=completed,
        ) as run:
            studio_local.run_command(["true"], timeout=0)

        self.assertIsNone(run.call_args.kwargs["timeout"])

    def test_command_timeout_must_not_be_negative(self) -> None:
        with unittest.mock.patch.object(studio_local.subprocess, "run") as run:
            with self.assertRaisesRegex(
                studio_local.StudioLocalError,
                "command timeout must be greater than or equal to 0",
            ):
                studio_local.run_command(["true"], timeout=-1)

        run.assert_not_called()

    def test_cli_rejects_negative_command_timeout_before_subcommand(self) -> None:
        stderr = io.StringIO()
        with unittest.mock.patch.object(studio_local, "command_check") as command_check, \
            contextlib.redirect_stderr(stderr):
            result = studio_local.run(["check", "--command-timeout", "-1", "--json"])

        self.assertEqual(result, 1)
        self.assertIn("command timeout must be greater than or equal to 0", stderr.getvalue())
        command_check.assert_not_called()

    def test_health_timeout_must_be_positive(self) -> None:
        with self.assertRaisesRegex(
            studio_local.StudioLocalError,
            "health timeout must be greater than 0",
        ):
            studio_local.studio_health("http://127.0.0.1:3900", 0)

    def test_log_tail_must_not_be_negative(self) -> None:
        stderr = io.StringIO()
        with unittest.mock.patch.object(studio_local, "require_binary") as require_binary, \
            contextlib.redirect_stderr(stderr):
            result = studio_local.run(["logs", "--tail", "-1"])

        self.assertEqual(result, 1)
        self.assertIn("log tail must be greater than or equal to 0", stderr.getvalue())
        require_binary.assert_not_called()

    def test_log_tail_zero_remains_explicitly_bounded(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"
        args.tail = 0
        args.command_timeout = 10

        with unittest.mock.patch.object(studio_local, "require_binary", return_value="/usr/bin/docker"), \
            unittest.mock.patch.object(
                studio_local,
                "compose_file",
                return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
            ), unittest.mock.patch.object(studio_local, "run_command") as run_command:
                studio_local.command_logs(args)

        self.assertEqual(run_command.call_args.args[0][-3:], ["logs", "--tail", "0"])

    def test_down_args_can_remove_volumes(self) -> None:
        args = unittest.mock.Mock()
        args.studio_dir = Path("/tmp/omnivoice-studio-src")
        args.profile = "cpu"

        with unittest.mock.patch.object(
            studio_local,
            "compose_file",
            return_value=Path("/tmp/omnivoice-studio-src/deploy/docker-compose.yml"),
        ):
            command = studio_local.compose_down_args(args, remove_volumes=True)

        self.assertEqual(command[-2:], ["down", "-v"])


class HermesSourceFinderTests(unittest.TestCase):
    def test_scores_likely_hermes_source_with_tts_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "hermes-agent"
            (repo / ".git").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "docs" / "tts.md").write_text(
                "Hermes TTS provider configuration for voice synthesis.",
                encoding="utf-8",
            )
            (repo / "pyproject.toml").write_text("[project]\nname='hermes-agent'\n", encoding="utf-8")

            report = source_finder.discover(
                argparse_namespace(
                    root=[root],
                    max_depth=3,
                    max_candidates=50,
                    max_files=100,
                    max_file_bytes=2048,
                    scan_timeout=20,
                )
            )

            self.assertEqual(report["likely_count"], 1)
            candidate = report["candidates"][0]
            self.assertTrue(candidate["likely_hermes_agent"])
            self.assertIn("docs/tts.md", candidate["tts_files"])

    def test_marks_this_bridge_repo_as_not_actual_agent_source(self) -> None:
        report = source_finder.discover(
            argparse_namespace(
                root=[Path(__file__).resolve().parents[1]],
                max_depth=1,
                max_candidates=50,
                max_files=500,
                max_file_bytes=2048,
                scan_timeout=20,
            )
        )

        self.assertEqual(report["likely_count"], 0)
        self.assertTrue(report["candidates"][0]["is_bridge_repo"])

    def test_discovery_skips_secret_named_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "hermes-agent"
            (repo / ".git").mkdir(parents=True)
            (repo / ".env").write_text("HERMES_TTS_PROVIDER=secret\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text("[project]\nname='hermes-agent'\n", encoding="utf-8")

            candidate = source_finder.inspect_candidate(repo, max_files=100, max_file_bytes=2048)

            self.assertNotIn(".env", candidate["tts_files"])

    def test_discovery_can_limit_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(3):
                repo = root / f"hermes-agent-{index}"
                (repo / ".git").mkdir(parents=True)
                (repo / "docs").mkdir()
                (repo / "docs" / "tts.md").write_text("Hermes TTS provider", encoding="utf-8")

            report = source_finder.discover(
                argparse_namespace(
                    root=[root],
                    max_depth=2,
                    max_candidates=1,
                    max_files=100,
                    max_file_bytes=2048,
                    scan_timeout=20,
                )
            )

            self.assertEqual(report["candidate_count"], 1)
            self.assertTrue(report["truncated"])

    def test_discovery_inspects_known_candidate_after_discovery_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "hermes-agent"
            (repo / ".git").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "docs" / "tts.md").write_text("Hermes TTS provider", encoding="utf-8")
            (repo / "pyproject.toml").write_text(
                "[project]\nname='hermes-agent'\n",
                encoding="utf-8",
            )

            with unittest.mock.patch.object(
                source_finder,
                "find_candidate_roots",
                return_value=([repo], True),
            ), unittest.mock.patch.object(
                source_finder.time,
                "monotonic",
                side_effect=[0, 10, 10, *([10.1] * 50)],
            ):
                report = source_finder.discover(
                    argparse_namespace(
                        root=[Path(tmp)],
                        max_depth=3,
                        max_candidates=50,
                        max_files=100,
                        max_file_bytes=2048,
                        scan_timeout=5,
                    )
                )

            self.assertTrue(report["truncated"])
            self.assertEqual(report["candidate_count"], 1)
            self.assertEqual(report["likely_count"], 1)

    def test_discovery_refuses_non_positive_scan_timeout(self) -> None:
        with self.assertRaisesRegex(
            source_finder.SourceDiscoveryError,
            "scan timeout must be greater than 0",
        ):
            source_finder.discover(
                argparse_namespace(
                    root=[Path("/tmp/missing-hermes-source")],
                    max_depth=3,
                    max_candidates=50,
                    max_files=100,
                    max_file_bytes=2048,
                    scan_timeout=0,
                )
            )

    def test_discovery_refuses_invalid_scan_bounds(self) -> None:
        cases = [
            ("max_depth", -1, "max depth must be at least 0"),
            ("max_candidates", 0, "max candidates must be greater than 0"),
            ("max_files", 0, "max files must be greater than 0"),
            ("max_file_bytes", 0, "max file bytes must be greater than 0"),
        ]
        for field, value, message in cases:
            with self.subTest(field=field):
                kwargs = {
                    "root": [Path("/tmp/missing-hermes-source")],
                    "max_depth": 3,
                    "max_candidates": 50,
                    "max_files": 100,
                    "max_file_bytes": 2048,
                    "scan_timeout": 20,
                }
                kwargs[field] = value
                with self.assertRaisesRegex(source_finder.SourceDiscoveryError, message):
                    source_finder.discover(argparse_namespace(**kwargs))

    def test_discovery_cli_invalid_scan_timeout_fails_without_traceback(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = source_finder.run(["--scan-timeout", "0", "--json"])

        self.assertEqual(result, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("find-hermes-source: scan timeout must be greater than 0", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


def argparse_namespace(**kwargs):
    return types.SimpleNamespace(**kwargs)


class ArtifactCheckTests(unittest.TestCase):
    def test_artifact_check_reports_generated_and_local_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "notes.md").write_text("safe", encoding="utf-8")
            (root / "sample.wav").write_bytes(b"not-a-real-wav")
            (root / "model.safetensors").write_bytes(b"model")
            (root / ".env.local").write_text("LOCAL_ONLY=redacted", encoding="utf-8")
            (root / "omnivoice-selection.json").write_text("{}", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "ignored.wav").write_bytes(b"ignored")

            matches = artifact_check.find_forbidden_artifacts(root)

            self.assertEqual(
                matches,
                [".env.local", "model.safetensors", "omnivoice-selection.json", "sample.wav"],
            )

    def test_artifact_check_cli_fails_when_matches_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text("local-only", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = artifact_check.run(["--root", str(root)])

            self.assertEqual(result, 1)
            self.assertIn(".env", stderr.getvalue())

    def test_artifact_check_reports_repo_local_artifact_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "models").mkdir()
            (root / "models" / "config.json").write_text("{}", encoding="utf-8")
            (root / ".cache").mkdir()
            (root / ".cache" / "blob").write_text("cache", encoding="utf-8")
            (root / ".hermes").mkdir()
            (root / ".hermes" / "voices.json").write_text("{}", encoding="utf-8")
            (root / "voices").mkdir()
            (root / "voices" / "local.yaml").write_text("id: local", encoding="utf-8")
            (root / "samples").mkdir()
            (root / "samples" / "transcript.txt").write_text("sample transcript", encoding="utf-8")
            (root / "voice-samples").mkdir()
            (root / "voice-samples" / "metadata.json").write_text("{}", encoding="utf-8")
            (root / "reference-audio").mkdir()
            (root / "reference-audio" / "readme.txt").write_text("local only", encoding="utf-8")
            (root / "examples" / "voices" / "narrator").mkdir(parents=True)
            (root / "examples" / "voices" / "narrator" / "voice.yaml").write_text(
                "id: narrator",
                encoding="utf-8",
            )

            matches = artifact_check.find_forbidden_artifacts(root)

            self.assertEqual(
                matches,
                [
                    ".cache/",
                    ".hermes/",
                    "models/",
                    "reference-audio/",
                    "samples/",
                    "voice-samples/",
                    "voices/",
                ],
            )

    def test_forbidden_root_dirs_have_ignore_coverage(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        repo_gitignore = set((repo_root / ".gitignore").read_text(encoding="utf-8").splitlines())
        installer_patterns = set(installer.GITIGNORE_PATTERNS)

        for dirname in artifact_check.FORBIDDEN_ROOT_DIRS:
            accepted_patterns = {f"{dirname}/", f"/{dirname}/"}
            self.assertTrue(
                accepted_patterns & installer_patterns,
                f"installer .gitignore coverage missing for {dirname}",
            )
            self.assertTrue(
                accepted_patterns & repo_gitignore,
                f"repo .gitignore coverage missing for {dirname}",
            )


class ValidationScriptTests(unittest.TestCase):
    def test_validator_smoke_backend_uses_configured_python_bin(self) -> None:
        script = VALIDATE_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn('SMOKE_COMMAND_JSON="$(', script)
        self.assertIn('"$PYTHON_BIN" - "$PYTHON_BIN"', script)
        self.assertIn('HERMES_OMNIVOICE_COMMAND_JSON="$SMOKE_COMMAND_JSON"', script)
        self.assertNotIn(
            '\'["python3","tests/fixtures/fake_omnivoice_backend.py"',
            script,
        )


class TerminologyTests(unittest.TestCase):
    def test_shipped_handoff_uses_omnivoice_studio_name(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        forbidden = "omni" + "vore"
        completed = subprocess.run(
            ["git", "ls-files", "README.md", "docs", "examples", "scripts"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        matches = []
        for relative_path in completed.stdout.splitlines():
            path = repo_root / relative_path
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if forbidden in text:
                matches.append(relative_path)

        self.assertEqual(matches, [])


class AcceptanceTests(unittest.TestCase):
    def test_acceptance_required_files_are_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report = acceptance.check_required_files(root)
        package_report = acceptance.check_required_files(root, acceptance.PACKAGE_REQUIRED_FILES)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["missing"], [])
        self.assertEqual(report["required_count"], len(installer.BASE_MANIFEST))
        self.assertEqual(package_report["status"], "pass")
        self.assertEqual(package_report["missing"], [])

    def test_acceptance_bridge_manifest_matches_installer_payload(self) -> None:
        self.assertEqual(
            set(acceptance.BRIDGE_REQUIRED_FILES),
            set(installer.BASE_MANIFEST),
        )

    def test_package_only_files_are_not_default_installer_payload(self) -> None:
        package_only = set(acceptance.PACKAGE_REQUIRED_FILES)

        self.assertTrue(package_only.isdisjoint(installer.BASE_MANIFEST))
        self.assertTrue(set(installer.EXAMPLE_MANIFEST).issubset(package_only))

    def test_acceptance_default_succeeds_without_real_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--json",
                    ],
                    env={},
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertTrue(report["mvp_static_ready"])
            self.assertEqual(report["package_files"]["status"], "pass")
            self.assertFalse(report["real_backend_ready"])
            self.assertFalse(report["hermes_source_ready"])

    def test_acceptance_runs_after_default_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                install_result = installer.run(["--target-root", str(target)])
            self.assertEqual(install_result, 0)

            spec = importlib.util.spec_from_file_location(
                "installed_omnivoice_acceptance",
                target / "scripts" / "omnivoice-acceptance.py",
            )
            assert spec is not None and spec.loader is not None
            installed_acceptance = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installed_acceptance)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = installed_acceptance.run(
                    [
                        "--voices-dir",
                        str(target / "missing-voices"),
                        "--source-root",
                        str(target / "missing-source"),
                        "--json",
                    ],
                    env={},
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertTrue(report["mvp_static_ready"])
            self.assertEqual(report["package_files"]["status"], "fail")
            self.assertFalse((target / "scripts" / "check-omnivoice-artifacts.py").exists())
            self.assertFalse((target / "scripts" / "validate-omnivoice-bridge.sh").exists())
            self.assertIn(
                "scripts/install-hermes-omnivoice-bridge.py",
                report["package_files"]["missing"],
            )

    def test_acceptance_human_output_marks_package_files_as_non_blocking_after_install(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                install_result = installer.run(["--target-root", str(target)])
            self.assertEqual(install_result, 0)

            spec = importlib.util.spec_from_file_location(
                "installed_omnivoice_acceptance_human",
                target / "scripts" / "omnivoice-acceptance.py",
            )
            assert spec is not None and spec.loader is not None
            installed_acceptance = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installed_acceptance)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = installed_acceptance.run(
                    [
                        "--voices-dir",
                        str(target / "missing-voices"),
                        "--source-root",
                        str(target / "missing-source"),
                    ],
                    env={},
                )

            text = output.getvalue()
            self.assertEqual(result, 0)
            self.assertIn(
                "- Local package handoff files: INCOMPLETE "
                "(package-only; not required after default install)",
                text,
            )
            self.assertIn(
                "Missing package-only files (only required with --require-package-files):",
                text,
            )
            self.assertNotIn("- Local package handoff files: BLOCKED", text)

    def test_acceptance_strict_package_files_still_fails_after_default_install(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                install_result = installer.run(["--target-root", str(target)])
            self.assertEqual(install_result, 0)

            spec = importlib.util.spec_from_file_location(
                "installed_omnivoice_acceptance_strict_package",
                target / "scripts" / "omnivoice-acceptance.py",
            )
            assert spec is not None and spec.loader is not None
            installed_acceptance = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installed_acceptance)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = installed_acceptance.run(
                    [
                        "--voices-dir",
                        str(target / "missing-voices"),
                        "--source-root",
                        str(target / "missing-source"),
                        "--require-package-files",
                    ],
                    env={},
                )

            text = output.getvalue()
            self.assertEqual(result, 1)
            self.assertIn(
                "- Local package handoff files: INCOMPLETE "
                "(package-only; not required after default install)",
                text,
            )
            self.assertIn(
                "Missing package-only files (only required with --require-package-files):",
                text,
            )

    def test_acceptance_can_require_real_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--require-real-backend",
                    ],
                    env={},
                )

            self.assertEqual(result, 1)
            self.assertIn("Real backend ready: BLOCKED", output.getvalue())

    def test_acceptance_invalid_runtime_command_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--json",
                    ],
                    env={
                        "HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(
                            ["/bin/echo", "{missing_placeholder}"]
                        )
                    },
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("omnivoice-acceptance:", error)
            self.assertIn("{missing_placeholder}", error)
            self.assertNotIn("Traceback", error)

    def test_acceptance_invalid_runtime_timeout_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--timeout",
                        "0",
                        "--json",
                    ],
                    env={},
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("omnivoice-acceptance:", error)
            self.assertIn("timeout must be greater than 0", error)
            self.assertNotIn("Traceback", error)

    def test_acceptance_invalid_source_scan_timeout_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--source-scan-timeout",
                        "0",
                        "--json",
                    ],
                    env={},
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("omnivoice-acceptance:", error)
            self.assertIn("scan timeout must be greater than 0", error)
            self.assertNotIn("Traceback", error)

    def test_acceptance_invalid_source_scan_bound_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--source-max-candidates",
                        "0",
                        "--json",
                    ],
                    env={},
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("omnivoice-acceptance:", error)
            self.assertIn("max candidates must be greater than 0", error)
            self.assertNotIn("Traceback", error)

    def test_acceptance_reports_missing_hermes_source_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            empty_source = Path(tmp) / "source"
            with contextlib.redirect_stdout(output):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(empty_source),
                        "--json",
                    ],
                    env={},
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertFalse(report["hermes_source_ready"])
            self.assertEqual(report["source_discovery"]["status"], "no_likely_hermes_agent")

    def test_acceptance_can_require_hermes_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(Path(tmp) / "missing"),
                        "--source-root",
                        str(Path(tmp) / "source"),
                        "--require-hermes-source",
                    ],
                    env={},
                )

            self.assertEqual(result, 1)
            self.assertIn("Hermes source ready: BLOCKED", output.getvalue())

    def test_acceptance_reports_likely_hermes_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "hermes-agent"
            (repo / ".git").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "docs" / "tts.md").write_text(
                "Hermes TTS provider configuration.",
                encoding="utf-8",
            )
            (repo / "pyproject.toml").write_text(
                "[project]\nname='hermes-agent'\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = acceptance.run(
                    [
                        "--voices-dir",
                        str(root / "missing"),
                        "--source-root",
                        str(root),
                        "--json",
                    ],
                    env={},
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertTrue(report["hermes_source_ready"])
            self.assertEqual(report["source_discovery"]["likely_count"], 1)


class InstallerTests(unittest.TestCase):
    def test_installer_dry_run_reports_manifest_without_copying(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = installer.run(
                    ["--target-root", str(target), "--dry-run", "--json"],
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertTrue(report["dry_run"])
            self.assertEqual(report["files"], len(installer.BASE_MANIFEST))
            self.assertEqual(report["gitignore"]["status"], "missing_patterns")
            self.assertEqual(report["gitignore"]["action"], "review")
            self.assertFalse((target / "scripts" / "hermes-omnivoice-tts.py").exists())
            self.assertFalse((target / ".gitignore").exists())

    def test_installer_copies_files_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                first = installer.run(["--target-root", str(target)])
            with contextlib.redirect_stderr(io.StringIO()):
                second = installer.run(["--target-root", str(target)])

            self.assertEqual(first, 0)
            self.assertEqual(second, 1)
            self.assertTrue((target / "scripts" / "hermes-omnivoice-tts.py").is_file())

    def test_installer_preserves_runtime_script_executable_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target)])

            self.assertEqual(result, 0)
            for relative_path in installer.BASE_MANIFEST:
                path = Path(relative_path)
                if path.parts[0] != "scripts" or path.suffix not in {".py", ".sh"}:
                    continue
                with self.subTest(relative_path=relative_path):
                    self.assertTrue(os.access(target / relative_path, os.X_OK))

    def test_installed_smoke_script_skips_without_backend_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target)])
            self.assertEqual(result, 0)

            env = os.environ.copy()
            for key in (
                "HERMES_OMNIVOICE_COMMAND_JSON",
                "HERMES_OMNIVOICE_COMMAND",
                "HERMES_OMNIVOICE_STUDIO_URL",
                "HERMES_OMNIVOICE_AUTO_CLI",
            ):
                env.pop(key, None)
            env["PYTHON_BIN"] = sys.executable

            completed = subprocess.run(
                [str(target / "scripts" / "test-omnivoice-tts.sh")],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 77)
            self.assertIn("SKIP: set HERMES_OMNIVOICE", completed.stderr)

    def test_installed_smoke_script_runs_with_configured_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target)])
            self.assertEqual(result, 0)

            command = [
                sys.executable,
                str(FAKE_BACKEND_PATH),
                "--text-file",
                "{text_file}",
                "--out",
                "{out}",
                "--voice-dir",
                "{voice_dir}",
                "--speed",
                "{speed}",
            ]
            env = os.environ.copy()
            env["HERMES_OMNIVOICE_COMMAND_JSON"] = json.dumps(command)
            env.pop("HERMES_OMNIVOICE_COMMAND", None)
            env.pop("HERMES_OMNIVOICE_STUDIO_URL", None)
            env.pop("HERMES_OMNIVOICE_AUTO_CLI", None)
            env["PYTHON_BIN"] = sys.executable

            completed = subprocess.run(
                [str(target / "scripts" / "test-omnivoice-tts.sh")],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("PASS: generated", completed.stdout)

    def test_installed_smoke_script_uses_private_temp_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target)])
            self.assertEqual(result, 0)

            backend_code = "\n".join(
                [
                    "import pathlib",
                    "import stat",
                    "import sys",
                    "import wave",
                    "out = pathlib.Path(sys.argv[1])",
                    "mode = stat.S_IMODE(out.stat().st_mode)",
                    "if out.name == 'hermes-output.wav' or not out.name.startswith('.hermes-output.wav.') or mode != 0o600:",
                    "    print(f'unsafe output path: {{out}} mode={{mode:o}}', file=sys.stderr)",
                    "    sys.exit(2)",
                    "with wave.open(str(out), 'wb') as wav:",
                    "    wav.setnchannels(1)",
                    "    wav.setsampwidth(2)",
                    "    wav.setframerate(16000)",
                    "    wav.writeframes(b'\\x00\\x00' * 160)",
                ]
            )
            command = [sys.executable, "-c", backend_code, "{out}"]
            env = os.environ.copy()
            env["HERMES_OMNIVOICE_COMMAND_JSON"] = json.dumps(command)
            env.pop("HERMES_OMNIVOICE_COMMAND", None)
            env.pop("HERMES_OMNIVOICE_STUDIO_URL", None)
            env.pop("HERMES_OMNIVOICE_AUTO_CLI", None)
            env["PYTHON_BIN"] = sys.executable

            completed = subprocess.run(
                [str(target / "scripts" / "test-omnivoice-tts.sh")],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PASS: generated", completed.stdout)

    def test_installer_can_include_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"

            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target), "--with-examples"])

            self.assertEqual(result, 0)
            self.assertTrue((target / "examples" / "hermes-tts-omnivoice.yaml").is_file())
            self.assertTrue((target / "examples" / "voices" / "narrator" / "voice.yaml").is_file())

    def test_installed_voice_helper_validates_example_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"

            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target), "--with-examples"])
            self.assertEqual(result, 0)

            voices_dir = target / "examples" / "voices"
            helper = target / "scripts" / "hermes-omnivoice-voices.py"
            narrator = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--voices-dir",
                    str(voices_dir),
                    "info",
                    "narrator",
                    "--json",
                ],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(narrator.returncode, 0, narrator.stderr)
            narrator_info = json.loads(narrator.stdout)
            self.assertEqual(narrator_info["id"], "narrator")
            self.assertEqual(narrator_info["mode"], "design")
            self.assertEqual(narrator_info["status"], "ready")
            self.assertEqual(narrator_info["consent_status"], "confirmed")

            marvin = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--voices-dir",
                    str(voices_dir),
                    "info",
                    "marvin",
                    "--json",
                ],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(marvin.returncode, 1)
            marvin_info = json.loads(marvin.stdout)
            self.assertEqual(marvin_info["id"], "marvin")
            self.assertEqual(marvin_info["status"], "invalid")
            self.assertIn("ref_audio is missing", marvin_info["error"])
            self.assertIn("ref.wav", marvin_info["error"])

    def test_installed_voice_helper_config_uses_installed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"

            with contextlib.redirect_stdout(io.StringIO()):
                result = installer.run(["--target-root", str(target), "--with-examples"])
            self.assertEqual(result, 0)

            voices_dir = target / "examples" / "voices"
            helper = target / "scripts" / "hermes-omnivoice-voices.py"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--voices-dir",
                    str(voices_dir),
                    "config",
                    "narrator",
                ],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(str(target / "scripts" / "hermes-omnivoice-tts.py"), completed.stdout)
            self.assertIn(f"--voices-dir {voices_dir}", completed.stdout)
            self.assertIn("voice: narrator", completed.stdout)

    def test_installer_can_append_gitignore_safety_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            target.mkdir()
            (target / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = installer.run(["--target-root", str(target), "--update-gitignore", "--json"])

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["gitignore"]["action"], "append")
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(installer.GITIGNORE_START, gitignore)
            self.assertIn("*.wav", gitignore)
            self.assertIn("/samples/", gitignore)
            self.assertIn("/voice-samples/", gitignore)
            self.assertIn("/reference-audio/", gitignore)
            self.assertIn("*.safetensors", gitignore)
            self.assertIn(".env.*", gitignore)
            self.assertIn(".env.local", gitignore)

            second = io.StringIO()
            with contextlib.redirect_stdout(second):
                rerun = installer.run(
                    ["--target-root", str(target), "--update-gitignore", "--force", "--json"]
                )

            second_report = json.loads(second.getvalue())
            self.assertEqual(rerun, 0)
            self.assertEqual(second_report["gitignore"]["status"], "managed")
            self.assertEqual(
                (target / ".gitignore").read_text(encoding="utf-8").count(installer.GITIGNORE_START),
                1,
            )

    def test_installer_can_update_managed_gitignore_safety_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            target.mkdir()
            old_block = "\n".join(
                [
                    installer.GITIGNORE_START,
                    "# Generated audio, local voices, model files, caches, and local config.",
                    "*.wav",
                    ".env",
                    installer.GITIGNORE_END,
                    "",
                ]
            )
            (target / ".gitignore").write_text(
                f"node_modules/\n\n{old_block}dist/\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = installer.run(["--target-root", str(target), "--update-gitignore", "--json"])

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["gitignore"]["status"], "managed_missing_patterns")
            self.assertEqual(report["gitignore"]["action"], "update")
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".env.*", gitignore)
            self.assertIn("/samples/", gitignore)
            self.assertIn("/voice-samples/", gitignore)
            self.assertIn("/reference-audio/", gitignore)
            self.assertIn("*.safetensors", gitignore)
            self.assertIn("node_modules/", gitignore)
            self.assertIn("dist/", gitignore)
            self.assertEqual(gitignore.count(installer.GITIGNORE_START), 1)

            second = io.StringIO()
            with contextlib.redirect_stdout(second):
                rerun = installer.run(
                    ["--target-root", str(target), "--update-gitignore", "--force", "--json"]
                )

            second_report = json.loads(second.getvalue())
            self.assertEqual(rerun, 0)
            self.assertEqual(second_report["gitignore"]["status"], "managed")
            self.assertEqual(second_report["gitignore"]["missing_patterns"], [])

    def test_installer_dry_run_reports_gitignore_append_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = installer.run(
                    ["--target-root", str(target), "--update-gitignore", "--dry-run", "--json"]
                )

            report = json.loads(output.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["gitignore"]["action"], "would_append")
            self.assertFalse((target / ".gitignore").exists())

    def test_installer_prints_human_gitignore_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hermes"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = installer.run(["--target-root", str(target), "--dry-run"])

            self.assertEqual(result, 0)
            self.assertIn("Review target .gitignore: missing", output.getvalue())

            append_output = io.StringIO()
            with contextlib.redirect_stdout(append_output):
                append_result = installer.run(
                    ["--target-root", str(target), "--update-gitignore", "--dry-run"]
                )

            self.assertEqual(append_result, 0)
            self.assertIn("Would append target .gitignore", append_output.getvalue())

            target.mkdir()
            old_block = "\n".join(
                [
                    installer.GITIGNORE_START,
                    "*.wav",
                    installer.GITIGNORE_END,
                    "",
                ]
            )
            (target / ".gitignore").write_text(old_block, encoding="utf-8")
            refresh_output = io.StringIO()

            with contextlib.redirect_stdout(refresh_output):
                refresh_result = installer.run(
                    ["--target-root", str(target), "--update-gitignore", "--dry-run"]
                )

            self.assertEqual(refresh_result, 0)
            self.assertIn("Would refresh target .gitignore", refresh_output.getvalue())

    def test_installer_rejects_target_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(installer.InstallError, "escapes"):
                installer.resolve_target(Path(tmp), "../outside")


class VoiceCliTests(unittest.TestCase):
    def test_list_profiles_marks_ready_and_invalid_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_voice(root, "marvin")
            invalid = root / "bad"
            invalid.mkdir()
            (invalid / "voice.yaml").write_text(
                "id: bad\nname: Bad\nengine: omnivoice\nmode: clone\n",
                encoding="utf-8",
            )

            profiles = voices_cli.list_profiles(root)
            by_id = {profile["id"]: profile for profile in profiles}

            self.assertEqual(by_id["marvin"]["status"], "ready")
            self.assertEqual(by_id["bad"]["status"], "invalid")

    def test_config_command_prints_command_provider_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_design_voice(root, "narrator")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = voices_cli.run(["--voices-dir", str(root), "config", "narrator"])

            self.assertEqual(result, 0)
            self.assertIn("provider: omnivoice", output.getvalue())
            self.assertIn("voice: narrator", output.getvalue())
            self.assertIn("speed: 1.0", output.getvalue())
            self.assertIn("output_format: wav", output.getvalue())
            self.assertIn("timeout: 180", output.getvalue())
            self.assertIn("voice_compatible: true", output.getvalue())
            self.assertIn("max_text_length: 2000", output.getvalue())
            self.assertIn("--voices-dir", output.getvalue())
            self.assertIn("--max-chars 2000", output.getvalue())

    def test_config_command_honors_timeout_and_max_text_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_design_voice(root, "narrator")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(root),
                        "config",
                        "narrator",
                        "--timeout",
                        "45",
                        "--max-text-length",
                        "512",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertIn("timeout: 45", output.getvalue())
            self.assertIn("max_text_length: 512", output.getvalue())
            self.assertIn("--max-chars 512", output.getvalue())

    def test_config_command_refuses_invalid_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_design_voice(root, "narrator")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(root),
                        "config",
                        "narrator",
                        "--timeout",
                        "0",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("timeout must be greater than 0", stderr.getvalue())

    def test_config_command_refuses_invalid_max_text_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_design_voice(root, "narrator")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(root),
                        "config",
                        "narrator",
                        "--max-text-length",
                        "0",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertIn("max text length must be greater than 0", stderr.getvalue())

    def test_config_command_includes_custom_voices_dir_and_quotes_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            voices_dir = Path(tmp) / "hermes voice roots" / "omnivoice"
            write_design_voice(voices_dir, "narrator")
            script_path = "/tmp/hermes bridge/hermes-omnivoice-tts.py"
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_dir),
                        "config",
                        "narrator",
                        "--script-path",
                        script_path,
                    ]
                )

            self.assertEqual(result, 0)
            config = output.getvalue()
            self.assertIn(f"--voices-dir {shlex.quote(str(voices_dir))}", config)
            self.assertIn(shlex.quote(script_path), config)
            self.assertIn("voice: narrator", config)

    def test_config_command_refuses_invalid_voice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / "bad"
            invalid.mkdir()
            (invalid / "voice.yaml").write_text(
                "id: bad\nname: Bad\nengine: omnivoice\nmode: clone\n",
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(["--voices-dir", str(root), "config", "bad"])

            self.assertEqual(result, 1)
            self.assertIn("Voice bad is invalid", stderr.getvalue())

    def test_preview_generates_audio_with_fake_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root, "marvin")
            out_file = root / "preview.wav"
            command = [
                sys.executable,
                str(FAKE_BACKEND_PATH),
                "--text-file",
                "{text_file}",
                "--out",
                "{out}",
                "--voice-dir",
                "{voice_dir}",
                "--speed",
                "{speed}",
            ]

            with unittest.mock.patch.dict(
                "os.environ",
                {"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(command)},
                clear=False,
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = voices_cli.run(
                        [
                            "--voices-dir",
                            str(voices_root),
                            "preview",
                            "marvin",
                            "--out",
                            str(out_file),
                        ]
                    )

            self.assertEqual(result, 0)
            self.assertIn("Preview written:", output.getvalue())
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)

    def test_preview_refuses_invalid_timeout_without_spawning_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root, "marvin")
            stderr = io.StringIO()

            with unittest.mock.patch.object(voices_cli.subprocess, "run") as run_mock:
                with contextlib.redirect_stderr(stderr):
                    result = voices_cli.run(
                        [
                            "--voices-dir",
                            str(voices_root),
                            "preview",
                            "marvin",
                            "--out",
                            str(root / "preview.wav"),
                            "--timeout",
                            "0",
                        ]
                    )

            self.assertEqual(result, 1)
            self.assertIn("timeout must be greater than 0", stderr.getvalue())
            run_mock.assert_not_called()

    def test_preview_refuses_invalid_speed_without_spawning_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            write_voice(voices_root, "marvin")
            stderr = io.StringIO()

            with unittest.mock.patch.object(voices_cli.subprocess, "run") as run_mock:
                with contextlib.redirect_stderr(stderr):
                    result = voices_cli.run(
                        [
                            "--voices-dir",
                            str(voices_root),
                            "preview",
                            "marvin",
                            "--out",
                            str(root / "preview.wav"),
                            "--speed",
                            "0",
                        ]
                    )

            self.assertEqual(result, 1)
            self.assertIn("speed must be greater than 0", stderr.getvalue())
            run_mock.assert_not_called()

    def test_set_and_current_commands_manage_selection_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            write_voice(voices_root, "marvin")

            with contextlib.redirect_stdout(io.StringIO()):
                set_result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                current_result = voices_cli.run(
                    [
                        "--selection-file",
                        str(selection_file),
                        "current",
                        "--json",
                    ]
                )

            payload = json.loads(selection_file.read_text(encoding="utf-8"))
            current = json.loads(output.getvalue())
            self.assertEqual(set_result, 0)
            self.assertEqual(current_result, 0)
            self.assertEqual(payload["provider"], "omnivoice")
            self.assertEqual(payload["voice"], "marvin")
            self.assertEqual(current["voice"], "marvin")
            self.assertEqual(current["status"], "ready")

    def test_set_command_writes_selection_file_with_private_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            write_voice(voices_root, "marvin")

            with contextlib.redirect_stdout(io.StringIO()):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )

            mode = stat.S_IMODE(selection_file.stat().st_mode)
            self.assertEqual(result, 0)
            self.assertEqual(mode, 0o600)

    def test_set_command_reports_selection_write_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            blocked_parent = root / "not-a-directory"
            blocked_parent.write_text("occupied", encoding="utf-8")
            selection_file = blocked_parent / "selection.json"
            write_voice(voices_root, "marvin")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )

            error = stderr.getvalue()
            self.assertEqual(result, 1)
            self.assertIn("hermes-omnivoice-voices:", error)
            self.assertNotIn("Traceback", error)

    def test_selection_file_write_cleans_temp_file_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection_file = Path(tmp) / "selection.json"

            with self.assertRaises(TypeError):
                voices_cli.write_selection_file(selection_file, {"bad": object()})

            leftovers = list(Path(tmp).glob(".selection.json.*.tmp"))
            self.assertFalse(selection_file.exists())
            self.assertEqual(leftovers, [])

    def test_set_command_replaces_selection_symlink_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            target = root / "target.json"
            write_voice(voices_root, "marvin")
            target.write_text("sentinel", encoding="utf-8")
            os.symlink(target, selection_file)

            with contextlib.redirect_stdout(io.StringIO()):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), "sentinel")
            self.assertFalse(selection_file.is_symlink())
            self.assertEqual(json.loads(selection_file.read_text(encoding="utf-8"))["voice"], "marvin")

    def test_current_command_reports_profile_speed_not_stale_selection_speed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            write_voice(voices_root, "marvin")

            with contextlib.redirect_stdout(io.StringIO()):
                set_result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )
            payload = json.loads(selection_file.read_text(encoding="utf-8"))
            payload["speed"] = 9.0
            selection_file.write_text(json.dumps(payload), encoding="utf-8")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                current_result = voices_cli.run(
                    [
                        "--selection-file",
                        str(selection_file),
                        "current",
                        "--json",
                    ]
                )

            current = json.loads(output.getvalue())
            self.assertEqual(set_result, 0)
            self.assertEqual(current_result, 0)
            self.assertEqual(current["speed"], 1.0)

    def test_current_command_refuses_stale_invalid_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            write_voice(voices_root, "marvin")

            with contextlib.redirect_stdout(io.StringIO()):
                set_result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "marvin",
                    ]
                )
            (voices_root / "marvin" / "ref.wav").unlink()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                current_result = voices_cli.run(
                    [
                        "--selection-file",
                        str(selection_file),
                        "current",
                    ]
                )

            self.assertEqual(set_result, 0)
            self.assertEqual(current_result, 1)
            self.assertIn("Selected OmniVoice voice marvin is invalid", stderr.getvalue())

    def test_current_command_refuses_malformed_selection_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection_file = Path(tmp) / "selection.json"
            selection_file.write_text(
                json.dumps({"provider": "omnivoice", "voice": "marvin", "voices_dir": []}),
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(["--selection-file", str(selection_file), "current"])

            self.assertEqual(result, 1)
            self.assertIn("Selection has invalid voices_dir", stderr.getvalue())

    def test_current_command_refuses_non_object_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection_file = Path(tmp) / "selection.json"
            selection_file.write_text(json.dumps(["omnivoice", "marvin"]), encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(["--selection-file", str(selection_file), "current"])

            self.assertEqual(result, 1)
            self.assertIn("Selection JSON must be an object", stderr.getvalue())

    def test_current_command_refuses_wrong_provider_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection_file = Path(tmp) / "selection.json"
            selection_file.write_text(
                json.dumps({"provider": "other", "voice": "marvin"}),
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                result = voices_cli.run(["--selection-file", str(selection_file), "current"])

            self.assertEqual(result, 1)
            self.assertIn("Selection provider is not omnivoice", stderr.getvalue())

    def test_set_command_refuses_invalid_voice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            voices_root = root / "voices"
            selection_file = root / "selection.json"
            invalid = voices_root / "bad"
            invalid.mkdir(parents=True)
            (invalid / "voice.yaml").write_text(
                "id: bad\nname: Bad\nengine: omnivoice\nmode: clone\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stderr(io.StringIO()):
                result = voices_cli.run(
                    [
                        "--voices-dir",
                        str(voices_root),
                        "--selection-file",
                        str(selection_file),
                        "set",
                        "bad",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertFalse(selection_file.exists())


class ExampleFileTests(unittest.TestCase):
    def test_tts_config_example_uses_ready_design_voice(self) -> None:
        config = (EXAMPLES_DIR / "hermes-tts-omnivoice.yaml").read_text(encoding="utf-8")

        self.assertIn("--voices-dir ~/.hermes/voices/omnivoice", config)
        self.assertIn("voice: narrator", config)
        self.assertIn("speed: 1.0", config)
        self.assertIn("output_format: wav", config)
        self.assertIn("timeout: 180", config)
        self.assertIn("voice_compatible: true", config)
        self.assertIn("max_text_length: 2000", config)
        self.assertNotIn("voice: marvin", config)

    def test_design_voice_example_validates(self) -> None:
        loaded, voice_dir = omnivoice.load_voice_profile(EXAMPLES_DIR / "voices", "narrator")
        validated = omnivoice.validate_voice_profile(loaded, voice_dir)

        self.assertEqual(validated["id"], "narrator")
        self.assertEqual(validated["consent"]["status"], "confirmed")

    def test_clone_voice_example_keeps_missing_audio_out_of_repo(self) -> None:
        loaded, voice_dir = omnivoice.load_voice_profile(EXAMPLES_DIR / "voices", "marvin")

        with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "ref_audio is missing"):
            omnivoice.validate_voice_profile(loaded, voice_dir)


if __name__ == "__main__":
    unittest.main()
