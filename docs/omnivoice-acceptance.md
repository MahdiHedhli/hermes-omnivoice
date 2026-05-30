# OmniVoice Acceptance Checklist

This repo separates two gates:

1. Static MVP readiness: the command bridge, registry tools, Studio bridge,
   docs, examples, tests, and heartbeat record are present.
2. Real backend readiness: a live local Studio service, configured backend
   command, or OmniVoice CLI is available, and at least one local voice profile
   exists.

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

For a strict live-runtime check:

```bash
python scripts/omnivoice-acceptance.py --require-real-backend
```

Current expected blocker on a fresh machine is real backend readiness. That is
resolved by starting loopback-only OmniVoice-Studio or configuring a local
OmniVoice command, then creating or importing at least one consented voice
profile under `~/.hermes/voices/omnivoice`.

Do not treat fake-backend tests as real synthesis acceptance. They only prove
wrapper I/O and WAV validation.
