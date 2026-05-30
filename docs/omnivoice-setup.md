# OmniVoice Setup

## Local Voice Registry

Create one directory per local voice:

```text
~/.hermes/voices/omnivoice/marvin/
  voice.yaml
  ref.wav
```

The safest way to create local profiles is the helper script. It refuses to
write a usable profile until consent is explicitly confirmed.

Create a designed voice:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --name Narrator \
  --instruct "calm male narrator, low pitch, clear delivery" \
  --confirm-consent
```

Create a cloned voice from a local WAV reference sample:

```bash
python scripts/create-omnivoice-voice.py clone marvin \
  --name Marvin \
  --ref-audio /path/to/consented-reference.wav \
  --ref-text "Reference transcript for the voice sample." \
  --confirm-consent
```

The clone command copies the reference sample into the local registry as
`ref.wav`, validates that the sample is a readable WAV file, and refuses to
write over an existing voice directory unless `--force` is set. Keep that
registry outside the repo.

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

Option A: point the wrapper at a local OmniVoice-Studio backend:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

The wrapper refuses non-loopback Studio URLs by default. Only set
`HERMES_OMNIVOICE_ALLOW_REMOTE_STUDIO=1` after Studio is protected by
authentication.

Option B: set a backend command. JSON is recommended:

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

Run all local bridge checks:

```bash
scripts/validate-omnivoice-bridge.sh
```

Run the smoke test only after configuring a real backend command:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[...]' scripts/test-omnivoice-tts.sh
```

Without a backend command, the smoke test exits `77` to mark the integration as
skipped rather than failed.

For CI or local contract testing without model weights, use the deterministic
test fixture backend:

```bash
HERMES_OMNIVOICE_COMMAND_JSON='[
  "python3",
  "tests/fixtures/fake_omnivoice_backend.py",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--voice-dir",
  "{voice_dir}",
  "--speed",
  "{speed}"
]' scripts/test-omnivoice-tts.sh
```

This verifies Hermes wrapper I/O and WAV validation only. It is not a real
OmniVoice synthesis quality test.

## Import A Studio Voice

After creating a profile in OmniVoice-Studio, import it into the Hermes registry:

```bash
python scripts/import-omnivoice-studio-voice.py \
  --studio-url http://127.0.0.1:3900 \
  --profile-id <studio-profile-id> \
  --voice-id marvin \
  --confirm-consent
```

The importer reads Studio through `GET /profiles/{id}` and
`GET /profiles/{id}/audio`, then writes
`~/.hermes/voices/omnivoice/<voice_id>/voice.yaml` and `ref.wav` when reference
audio is available. It refuses existing non-empty voice directories unless
`--force` is set, and downloaded reference audio must be a valid WAV.

## Inspect And Preview Voices

List local voices:

```bash
python scripts/hermes-omnivoice-voices.py list
```

Inspect one voice and verify consent state:

```bash
python scripts/hermes-omnivoice-voices.py info marvin
```

Generate a short preview:

```bash
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
```

Print a Hermes command-provider config example:

```bash
python scripts/hermes-omnivoice-voices.py config marvin
```
