# OmniVoice Acceptance Checklist

This repo separates three gates:

1. Static MVP readiness: the command bridge, registry tools, Studio bridge,
   docs, examples, tests, and heartbeat record are present.
2. Real backend readiness: a live local Studio service, configured backend
   command, or OmniVoice CLI is available, and at least one local voice profile
   exists.
3. Hermes source readiness: a bounded read-only discovery pass has found a
   likely Hermes Agent checkout for final command-provider or native-provider
   wiring.

Run:

```bash
scripts/validate-omnivoice-bridge.sh
python scripts/omnivoice-acceptance.py
```

For handoff into a real Hermes checkout, dry-run the installer first:

```bash
python scripts/install-hermes-omnivoice-bridge.py \
  --target-root /path/to/hermes-agent \
  --dry-run
```

Use `docs/omnivoice-mvp-handoff.md` for the current package state, live
blockers, install path, and the commands needed to move from static acceptance
to real synthesis acceptance.

The acceptance command runs source discovery by default with a short timeout.
To point it at an explicit checkout root:

```bash
python scripts/omnivoice-acceptance.py \
  --source-root /path/to/search
```

For a strict Hermes-source check:

```bash
python scripts/omnivoice-acceptance.py --require-hermes-source
```

For a strict live-runtime check:

```bash
python scripts/omnivoice-acceptance.py --require-real-backend
```

Current expected blockers on a fresh machine are Hermes source readiness and
real backend readiness. Hermes source readiness is resolved by running the
installer or final wiring from an actual Hermes Agent checkout. Real backend
readiness is resolved by starting loopback-only OmniVoice-Studio or configuring
a local OmniVoice command, by pointing `HERMES_OMNIVOICE_COMMAND_JSON` at
`scripts/hermes-omnivoice-python-adapter.py`, or by installing `omnivoice-infer`
and setting `HERMES_OMNIVOICE_AUTO_CLI=1`, then creating or importing at least
one consented voice profile under `~/.hermes/voices/omnivoice`.

Use `python scripts/setup-omnivoice-python-env.py --dry-run` before creating
the local Python backend environment. Use `--check-only --require-ready` after
installation when the Python API path should be considered ready. If the dry-run
selects an unsupported Python, rerun it with `--python` pointing at Python 3.10
through 3.13.

On the current Mac, the isolated Python backend venv is already ready under
`~/.cache/hermes/omnivoice-python`, but the default shell still has no exported
backend command and no persistent local voices. The Studio Docker path remains
blocked by the published image's missing arm64 manifest and by a source build
that exceeded the heartbeat timeout before image export completed.

Do not treat fake-backend tests as real synthesis acceptance. They only prove
wrapper I/O and WAV validation.
