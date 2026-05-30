from __future__ import annotations

import contextlib
import http.server
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import unittest.mock
import wave


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hermes-omnivoice-tts.py"
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
STUDIO_LOCAL_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "omnivoice-studio-local.py"
)
FAKE_BACKEND_PATH = Path(__file__).resolve().parent / "fixtures" / "fake_omnivoice_backend.py"
EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
SPEC = importlib.util.spec_from_file_location("hermes_omnivoice_tts", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
omnivoice = importlib.util.module_from_spec(SPEC)
sys.modules["hermes_omnivoice_tts"] = omnivoice
SPEC.loader.exec_module(omnivoice)

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

STUDIO_LOCAL_SPEC = importlib.util.spec_from_file_location(
    "omnivoice_studio_local", STUDIO_LOCAL_SCRIPT_PATH
)
assert STUDIO_LOCAL_SPEC is not None and STUDIO_LOCAL_SPEC.loader is not None
studio_local = importlib.util.module_from_spec(STUDIO_LOCAL_SPEC)
sys.modules["omnivoice_studio_local"] = studio_local
STUDIO_LOCAL_SPEC.loader.exec_module(studio_local)


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 160)


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
instruct: "calm local assistant, clear delivery"
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
            with wave.open(str(out_file), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertGreater(wav.getnframes(), 0)

    def test_studio_url_must_be_loopback_by_default(self) -> None:
        with self.assertRaisesRegex(omnivoice.OmniVoiceConfigError, "non-loopback"):
            omnivoice.validate_studio_url("http://10.0.0.5:3900", {})

    def test_studio_url_accepts_loopback(self) -> None:
        self.assertEqual(
            omnivoice.validate_studio_url("http://127.0.0.1:3900/", {}),
            "http://127.0.0.1:3900",
        )

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
            with wave.open(str(out_file), "rb") as wav:
                self.assertGreater(wav.getnframes(), 0)


class OmniVoiceIntegrationTests(unittest.TestCase):
    def test_real_omnivoice_backend_is_configured(self) -> None:
        self.skipTest(
            "Configure HERMES_OMNIVOICE_COMMAND_JSON or HERMES_OMNIVOICE_COMMAND "
            "with a real OmniVoice backend to run integration synthesis."
        )


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
                        "calm local assistant voice",
                        "--confirm-consent",
                    ]
                )

            self.assertEqual(result, 0)
            loaded, voice_dir = omnivoice.load_voice_profile(voices_root, "narrator")
            validated = omnivoice.validate_voice_profile(loaded, voice_dir)
            self.assertEqual(validated["mode"], "design")
            self.assertEqual(validated["consent"]["source"], "user_created")

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

    def test_runtime_check_redacts_backend_command_arguments(self) -> None:
        report = runtime_check.check_backend_command(
            {"HERMES_OMNIVOICE_COMMAND_JSON": json.dumps(["/bin/echo", "secret-arg"])}
        )

        encoded = json.dumps(report)
        self.assertEqual(report["status"], "configured")
        self.assertEqual(report["mode"], "command_json")
        self.assertIn("echo", report["executable"])
        self.assertNotIn("secret-arg", encoded)

    def test_runtime_check_rejects_remote_studio_by_default(self) -> None:
        with self.assertRaisesRegex(runtime_check.RuntimeCheckError, "non-loopback"):
            runtime_check.validate_studio_url("http://10.0.0.5:3900")

    def test_runtime_check_accepts_loopback_studio_profiles(self) -> None:
        with mock_studio_server() as (studio_url, requests):
            report = runtime_check.check_studio(studio_url, 5, False)

        self.assertEqual(report["status"], "reachable")
        self.assertEqual(report["profile_count"], 1)
        self.assertEqual(requests[0]["path"], "/profiles")


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
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = voices_cli.run(["config", "marvin"])

        self.assertEqual(result, 0)
        self.assertIn("provider: omnivoice", output.getvalue())
        self.assertIn("voice: marvin", output.getvalue())

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


class ExampleFileTests(unittest.TestCase):
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
