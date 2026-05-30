# OmniVoice Setup

## Local Voice Registry

Create one directory per local voice:

```text
~/.hermes/voices/omnivoice/marvin/
  voice.yaml
  ref.wav
```

Example clone profile:

```yaml
id: marvin
name: Marvin
engine: omnivoice
mode: clone
ref_audio: ref.wav
ref_text: "Reference transcript for the voice sample."
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_uploaded
  allowed_uses:
    - personal_assistant
    - local_generation
```

Example designed profile:

```yaml
id: narrator
name: Narrator
engine: omnivoice
mode: design
instruct: "calm male narrator, low pitch, clear delivery"
language: en
speed: 1.0
consent:
  status: confirmed
  source: user_created
  allowed_uses:
    - personal_assistant
    - local_generation
```

## Configure A Backend

Set a backend command before using the wrapper. JSON is recommended:

```bash
export HERMES_OMNIVOICE_COMMAND_JSON='[
  "python",
  "-m",
  "your_omnivoice_adapter",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--voice-dir",
  "{voice_dir}",
  "--speed",
  "{speed}"
]'
```

Then run:

```bash
python scripts/hermes-omnivoice-tts.py \
  --text-file /tmp/hermes-input.txt \
  --out /tmp/hermes-output.wav \
  --voice marvin \
  --speed 1.0
```

The wrapper exits non-zero if the profile is invalid, consent is missing, the
reference audio is missing, the backend command fails, or the output WAV is not
valid.

## Smoke Test

Run the smoke test only after configuring a real backend command:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh
```

Without a backend command, the smoke test exits `77` to mark the integration as
skipped rather than failed.
