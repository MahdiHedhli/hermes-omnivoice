# Hermes Custom Voices

## Command Provider Example

The exact Hermes TTS schema still needs to be verified against the real Hermes
Agent source. The intended shape is:

```yaml
tts:
  provider: omnivoice
  providers:
    omnivoice:
      type: command
      command: "python scripts/hermes-omnivoice-tts.py --voice {voice} --speed {speed} --text-file {input_path} --out {output_path}"
      voice: marvin
      output_format: wav
      timeout: 180
      voice_compatible: true
      max_text_length: 2000
```

If Hermes uses different placeholder names, adapt the command string to the real
schema while preserving:

- text input path
- output audio path
- voice ID
- speed
- timeout
- output format

## Studio API Example

If Hermes can pass environment variables to command providers, Studio can be the
backend without a custom command adapter:

```bash
export HERMES_OMNIVOICE_STUDIO_URL=http://127.0.0.1:3900
```

Then use the same command provider invocation:

```yaml
tts:
  provider: omnivoice
  providers:
    omnivoice:
      type: command
      command: "python scripts/hermes-omnivoice-tts.py --voice {voice} --speed {speed} --text-file {input_path} --out {output_path}"
      voice: marvin
      output_format: wav
      timeout: 180
```

For Studio-created voices, import the profile first with
`scripts/import-omnivoice-studio-voice.py`.

For local non-Studio profiles, create a consented registry entry with:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --instruct "calm local assistant voice" \
  --confirm-consent

python scripts/create-omnivoice-voice.py clone marvin \
  --ref-audio /path/to/consented-reference.wav \
  --ref-text "Reference transcript for the voice sample." \
  --confirm-consent
```

## Python API Backend Example

If the Hermes runtime has `omnivoice` installed, use the packaged Python adapter
as a backend command:

```bash
export HERMES_OMNIVOICE_COMMAND_JSON='[
  "python3",
  "scripts/hermes-omnivoice-python-adapter.py",
  "--text-file",
  "{text_file}",
  "--out",
  "{out}",
  "--ref-audio",
  "{ref_audio}",
  "--ref-text",
  "{ref_text}",
  "--instruct",
  "{instruct}",
  "--language",
  "{language}",
  "--speed",
  "{speed}"
]'
```

The wrapper validates the voice profile first, then passes clone or design
fields to the adapter.

## Operational Notes

- Store voice profiles outside the repo under `~/.hermes/voices/omnivoice`.
- Keep generated media and reference samples out of git.
- Use readable WAV reference samples for cloned voices.
- Use local synthesis only unless a separate security review approves a remote
  service.
- Treat cloned voice consent as a hard gate, not a documentation-only field.

## Voice Helper CLI

This repo includes a local helper for the UX commands Hermes may eventually
surface natively:

```bash
python scripts/hermes-omnivoice-voices.py list
python scripts/hermes-omnivoice-voices.py info marvin
python scripts/hermes-omnivoice-voices.py set marvin
python scripts/hermes-omnivoice-voices.py current
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
python scripts/hermes-omnivoice-voices.py config marvin
```

The preview command uses `scripts/hermes-omnivoice-tts.py`, so it requires the
same local Studio URL or backend command configuration as Hermes TTS. The
`set` command validates consent and writes `~/.hermes/omnivoice-selection.json`
for user-level selection state. The `config` command prints a command-provider
YAML example for the selected voice.
