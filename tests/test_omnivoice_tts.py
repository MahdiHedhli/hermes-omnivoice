from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "hermes-omnivoice-tts.py"
SPEC = importlib.util.spec_from_file_location("hermes_omnivoice_tts", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
omnivoice = importlib.util.module_from_spec(SPEC)
sys.modules["hermes_omnivoice_tts"] = omnivoice
SPEC.loader.exec_module(omnivoice)


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


if __name__ == "__main__":
    unittest.main()
