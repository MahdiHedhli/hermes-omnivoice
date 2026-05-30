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

## Operational Notes

- Store voice profiles outside the repo under `~/.hermes/voices/omnivoice`.
- Keep generated media and reference samples out of git.
- Use local synthesis only unless a separate security review approves a remote
  service.
- Treat cloned voice consent as a hard gate, not a documentation-only field.
