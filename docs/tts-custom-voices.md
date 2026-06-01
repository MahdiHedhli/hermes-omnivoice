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
      command: "python scripts/hermes-omnivoice-tts.py --voices-dir ~/.hermes/voices/omnivoice --voice {voice} --speed {speed} --max-chars 2000 --text-file {input_path} --out {output_path}"
      voice: narrator
      speed: 1.0
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
- max text length
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
      command: "python scripts/hermes-omnivoice-tts.py --voices-dir ~/.hermes/voices/omnivoice --voice {voice} --speed {speed} --max-chars 2000 --text-file {input_path} --out {output_path}"
      voice: narrator
      speed: 1.0
      output_format: wav
      timeout: 180
```

For Studio-created voices, import the profile first with
`scripts/import-omnivoice-studio-voice.py`.

For local non-Studio profiles, create a consented registry entry with:

```bash
python scripts/create-omnivoice-voice.py design narrator \
  --instruct "male, american accent, moderate pitch" \
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
fields to the adapter. The adapter also rejects non-finite or non-positive
speed values and non-positive sample rates before loading the OmniVoice Python
backend, and reports invalid backend sample rates as adapter errors instead of
raw conversion exceptions. Empty model, device, and dtype values are rejected
before model loading.

Prepare or inspect the adapter environment outside the repo with:

```bash
python scripts/setup-omnivoice-python-env.py --dry-run
python scripts/setup-omnivoice-python-env.py --check-only
python scripts/setup-omnivoice-python-env.py --check-only --shell
```

The setup helper rejects empty model and package values before it prints shell
exports or plans pip commands.

Use `--python` with a Python 3.10 through 3.13 interpreter if the default
`python3` on the machine is newer than the current OmniVoice runtime stack.

## Operational Notes

- Store voice profiles outside the repo under `~/.hermes/voices/omnivoice`.
- Keep generated media and reference samples out of git.
- Use readable WAV reference samples for cloned voices.
- Use local synthesis only unless a separate security review approves a remote
  service.
- Do not put credentials in Studio URLs; wrapper, importer, and runtime
  diagnostics reject URL userinfo.
- The Studio importer rejects non-loopback or credential-bearing Studio URLs
  before it creates local registry directories or contacts Studio.
- The Studio importer rejects empty profile IDs before local writes or network
  access, and cloned Studio profiles must include reference text before
  imported `ref.wav` or `voice.yaml` material is written.
- Keep importer `--timeout` greater than zero; invalid values fail before local
  registry writes or Studio network access.
- Keep `speed` finite and greater than zero, and keep wrapper `timeout` greater
  than zero; malformed runtime values fail before backend startup.
- The profile creation helper rejects non-finite or non-positive `--speed`
  values and empty `--allowed-use` values before it creates local profile
  directories or copies clone reference audio.
- Voice profiles must carry confirmed consent with non-empty `consent.source`
  and at least one non-empty `consent.allowed_uses` entry. The profile creation
  helper rejects empty `--consent-source` values before it writes local profile
  material.
- Keep wrapper `--max-chars` aligned with Hermes `max_text_length`; oversized
  input files fail before backend startup.
- Generated command-provider config refuses non-positive `timeout` and
  `max_text_length` overrides before printing YAML.
- Treat cloned voice consent as a hard gate, not a documentation-only field.
- Use the profile helpers for local registry writes. They create voice profile
  directories with `0700` permissions and write `voice.yaml` plus copied or
  imported `ref.wav` files with `0600` permissions. Forced rewrites replace
  existing material symlinks instead of following them.
- Generated audio may contain sensitive assistant output. The wrapper removes
  an existing output symlink before synthesis, passes command backends a
  private temporary output path, and leaves successful output files with `0600`
  permissions. Command and Studio API outputs are validated before atomic
  replacement.

## Voice Helper CLI

This repo includes a local helper for the UX commands Hermes may eventually
surface natively:

```bash
python scripts/hermes-omnivoice-voices.py list
python scripts/hermes-omnivoice-voices.py info marvin
python scripts/hermes-omnivoice-voices.py set marvin
python scripts/hermes-omnivoice-voices.py current
python scripts/hermes-omnivoice-voices.py preview marvin --out /tmp/marvin-preview.wav
python scripts/hermes-omnivoice-voices.py config narrator
```

The preview command uses `scripts/hermes-omnivoice-tts.py`, so it requires the
same local Studio URL or backend command configuration as Hermes TTS. The
preview helper validates `--speed` and `--timeout` overrides before launching
the wrapper subprocess. The
`set` command validates consent and writes `~/.hermes/omnivoice-selection.json`
for user-level selection state using a private `0600` atomic same-directory
replace. Existing destination symlinks are replaced instead of followed. The
helper cleans up failed temporary writes before returning the error. The
top-level helper returns concise `hermes-omnivoice-voices:` errors for local
filesystem or subprocess failures instead of Python tracebacks. The
`current` command revalidates that selected profile before reporting it, so
stale or invalid local selection state fails closed, including malformed
registry pointer metadata and non-OmniVoice selection records. It reports
profile-derived speed and registry path instead of trusting stale values from
the selection file. The `config` command prints a command-provider YAML example
for the selected voice and includes the configured `--voices-dir` path in the
generated wrapper command. It refuses missing or invalid profiles instead of
printing config that Hermes would fail at runtime.
