🎙️ **OmniVoice for Hermes** — self-hosted, ElevenLabs-tier voice for your agent

Shipped a **native Hermes TTS plugin** for OmniVoice / OmniVoice-Studio. Clone a voice from a short sample, design one from attributes, then **preview, edit, and select** it — all from the dashboard. No per-token cost, no rate limits, and your reference audio never leaves your machine.

**Install — one command:**
```
hermes plugins install MahdiHedhli/hermes-omnivoice/omnivoice
hermes gateway restart
```

**What you get**
• `tts.provider: omnivoice` routes **every** `text_to_speech` call, voice-mode reply, Discord VC utterance, and messaging voice through OmniVoice — zero per-surface wiring
• A dashboard **Voices** tab: clone / design / **edit** / preview / select, with a clickable attribute guide + validation (no more free words that silently fail at synth)
• A new **Talk** tab 🎙️ — hold a spoken conversation with your agent right in the browser: it transcribes you, runs the *real* Hermes agent (tools + memory via `--resume`), and replies **out loud in your active voice**
• **3 backends** — `local` (in-process), `studio` (loopback server), `service` (LAN/tailnet node w/ bearer auth + ssh-loopback). The included OpenAI-compatible model server is the *same artifact* from one host to a shared fleet.
• Consent gate + path hardening on clone ingestion, MPS-memory-safe synthesis, and an ASR "does it actually speak?" QC check

Built entirely on the native `TTSProvider` + dashboard-plugin surfaces — **no forks**. Tested live on Hermes v0.18.

Repo + full guide 👉 <https://github.com/MahdiHedhli/hermes-omnivoice>

Feedback and issues welcome 🙏 (demo below 👇)
