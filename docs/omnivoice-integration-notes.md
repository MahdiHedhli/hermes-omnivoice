# OmniVoice Integration Notes

## Discovery Snapshot

The scheduled workspace was empty at the first heartbeat, so this bridge is being
implemented as a fresh, standalone command-provider integration instead of
editing Hermes Agent internals directly.

Findings:

- The current directory had no `.git` directory, source tree, docs, tests, or
  Hermes TTS implementation to inspect.
- No local Hermes Agent source was present under the scheduled workspace.
- Follow-up local checks also found no `/opt/hermes-agent/source` and no readable
  `~/.hermes` config files in this environment.
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

This keeps Hermes behavior unchanged and avoids binding any Studio service to
the LAN. After inspecting OmniVoice-Studio, the wrapper now also supports a
localhost-only Studio API mode through `HERMES_OMNIVOICE_STUDIO_URL`.

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

## Acceptance Gates

Use `scripts/validate-omnivoice-bridge.sh` for deterministic local contract
tests, then `scripts/omnivoice-acceptance.py` to summarize whether the static
MVP is present and whether a real local backend plus voice profile are ready.

## Voice UX Bridge

The scheduled workspace does not include Hermes command/plugin UX source, so the
project now ships a standalone helper that maps cleanly to the proposed future
commands:

- `scripts/hermes-omnivoice-voices.py list`
- `scripts/hermes-omnivoice-voices.py info <voice_id>`
- `scripts/hermes-omnivoice-voices.py preview <voice_id> --out <path>`
- `scripts/hermes-omnivoice-voices.py config <voice_id>`

If Hermes has a command/plugin layer in the real source tree, these operations
can be wired behind `/voice list`, `/voice info`, `/voice preview`, and a config
selection command without changing the registry contract.

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

## OmniVoice-Studio API Findings

The current OmniVoice-Studio source exposes a FastAPI backend on port `3900`.
Relevant routes:

- `GET /profiles`: list saved voice profiles.
- `GET /profiles/{profile_id}`: read a full voice profile row.
- `GET /profiles/{profile_id}/audio`: download the profile reference or locked
  audio.
- `POST /generate`: synthesize WAV audio from text, `profile_id`, `ref_audio`,
  `ref_text`, `instruct`, language, and speed form fields.
- `GET /v1/audio/voices`: OpenAI-compatible extension listing available voices.
- `POST /v1/audio/speech`: OpenAI-compatible speech synthesis.

The Studio SQLite table is named `voice_profiles`, with fields including `id`,
`name`, `ref_audio_path`, `ref_text`, `instruct`, `language`,
`locked_audio_path`, `seed`, and `is_locked`. The bridge should use the HTTP
API before reading this database directly.

Security note: the Docker Compose file binds host port `3900` to
`127.0.0.1:3900` by default and explicitly states that Studio has no built-in
authentication. The package `dev:api` script uses `--host 0.0.0.0`; for Hermes
integration, run Studio on loopback unless a separate authenticated reverse
proxy is deliberately configured.
