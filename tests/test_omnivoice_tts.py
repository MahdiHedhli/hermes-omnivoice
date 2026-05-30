from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
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
FAKE_BACKEND_PATH = Path(__file__).resolve().parent / "fixtures" / "fake_omnivoice_backend.py"
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


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 160)


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


if __name__ == "__main__":
    unittest.main()
