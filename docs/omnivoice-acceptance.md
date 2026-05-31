# OmniVoice Acceptance Checklist

This repo separates three gates:

1. Static MVP readiness: the installed command bridge, registry tools, Studio
   bridge, runtime checks, and handoff docs are present.
2. Real backend readiness: a live local Studio service, configured backend
   command, or OmniVoice CLI is available, and at least one local voice profile
   exists.
3. Hermes source readiness: a bounded read-only discovery pass has found a
   likely Hermes Agent checkout for final command-provider or native-provider
   wiring.

It also reports local package-only handoff files, such as the installer,
validation script, examples, and heartbeat record. Those package extras are
required in this bridge repo but are not required after a default install into a
real Hermes checkout.

Run:

```bash
scripts/validate-omnivoice-bridge.sh
python scripts/omnivoice-acceptance.py
```

The validation script runs the deterministic test suite, smoke checks,
secret-pattern scanning, generated-artifact scanning for audio/model/env/local
selection files, and whitespace checks.

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

Use explicit candidate roots or `scripts/find-hermes-source.py` for handoff
evidence. Broad content searches across a whole workspace are too noisy because
unrelated repos often contain generic `voice`, `tts`, or `provider` text.

For a strict Hermes-source check:

```bash
python scripts/omnivoice-acceptance.py --require-hermes-source
```

For a strict live-runtime check:

```bash
python scripts/omnivoice-acceptance.py --require-real-backend
```

For a strict local package handoff check in this repo:

```bash
python scripts/omnivoice-acceptance.py --require-package-files
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
through 3.13. Use `--check-only --shell` to print safely quoted exports for the
prepared adapter command.

On the current Mac, the isolated Python backend venv is ready under
`~/.cache/hermes/omnivoice-python` and a consented designed profile exists under
`~/.hermes/voices/omnivoice/heartbeat_narrator`. Strict real-backend acceptance
passes when the prepared adapter command is exported, and the smoke test has
generated a valid temporary WAV through that path. The default shell still has
no exported backend command, so default acceptance does not claim live backend
readiness. The Studio Docker path remains blocked by the published image's
missing arm64 manifest and by a source build that exceeded the heartbeat
timeout before image export completed.

Do not treat fake-backend tests as real synthesis acceptance. They only prove
wrapper I/O and WAV validation.
