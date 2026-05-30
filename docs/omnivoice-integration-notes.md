# OmniVoice Integration Notes

## Discovery Snapshot

The scheduled workspace was empty at the first heartbeat, so this bridge is being
implemented as a fresh, standalone command-provider integration instead of
editing Hermes Agent internals directly.

Findings:

- The current directory had no `.git` directory, source tree, docs, tests, or
  Hermes TTS implementation to inspect.
- No local Hermes Agent source was present under the scheduled workspace.
- The least invasive path is a command-provider MVP: Hermes writes input text to
  a file, calls `scripts/hermes-omnivoice-tts.py`, and consumes the generated
  audio file.
- A future heartbeat should inspect the real Hermes Agent repo or installed
  source before attempting a native provider.

## MVP Decision

Use a local voice registry and explicit backend command configuration:

```text
Hermes Agent
  -> command TTS provider
  -> scripts/hermes-omnivoice-tts.py
  -> HERMES_OMNIVOICE_COMMAND_JSON or HERMES_OMNIVOICE_COMMAND
  -> OmniVoice or OmniVoice-Studio local backend
  -> output WAV returned to Hermes
```

This keeps Hermes behavior unchanged, avoids binding any Studio service to the
LAN, and lets the real OmniVoice invocation be swapped once the backend API is
verified.

## Registry Contract

Voice profiles live under:

```text
~/.hermes/voices/omnivoice/<voice_id>/voice.yaml
~/.hermes/voices/omnivoice/<voice_id>/ref.wav
```

The wrapper currently supports:

- `mode: clone` with `ref_audio` and `ref_text`
- `mode: design` with `instruct`
- `consent.status: confirmed`
- voice IDs containing only letters, numbers, `.`, `_`, and `-`

The clone path refuses to run when the reference audio is missing or consent is
not confirmed.

## Backend Command Contract

Prefer `HERMES_OMNIVOICE_COMMAND_JSON` because it avoids shell quoting issues:

```json
[
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
]
```

Available placeholders:

- `{text_file}` or `{input_path}`
- `{out}` or `{output_path}`
- `{voice}` or `{voice_id}`
- `{voice_dir}`
- `{speed}`
- `{language}`
- `{ref_audio}`
- `{ref_text}`
- `{instruct}`

`HERMES_OMNIVOICE_COMMAND` is also supported for a shell-style string, but the
wrapper still executes without `shell=True`.
