🎙️ **OmniVoice for Hermes — update:** talk to your agent, a voice library, and ~2× faster speech

Follow-up to the [original post](https://github.com/MahdiHedhli/hermes-omnivoice). Four things landed since:

**🗣️ Talk to your agent, out loud**
A new **Talk** tab: hit record (or type), the *real* Hermes agent answers — same tools, same session, `--resume` continuity — and the reply plays back in your active voice. It keeps replies short on purpose and speaks them **sentence-by-sentence**, synthesizing the next while the current one plays, so you hear the first words in one sentence's time instead of waiting out the whole answer.

**🖼️ A voice library, one click**
A **Gallery** tab with **24 ready-made designed voices** — The Librarian, The Storyteller, Captain Crusty, The Anchor … — grouped by use case. *Add to my voices* drops one into your registry as a normal design voice you can preview, edit, or set active. They **ship inside the plugin**, so the tab works with no network at all; *Refresh from gallery* is the only outbound call and only when you click it. (Text-only presets only — pulling third-party recordings of real people would route around the consent gate the clone path exists to enforce.)

**⚡ ~2× faster synthesis, measured**
OmniVoice is a *diffusion* model — it denoises each generation over `num_step` passes, and that count is the real speed dial. Timed on Apple Silicon, same phrase, transcript ASR-checked at every setting:

```
num_step=32 (SDK default)  36.6s   reference transcript
num_step=16 (new default)  19.4s   identical transcript
num_step=8                 11.4s   starts dropping words
num_step=4                  6.3s   broken
```

Same speech, roughly half the time. Two non-levers, in case you go chasing them: `device: auto` already picks MPS (~3.3× faster than CPU here), and there is **no MLX build** of OmniVoice — it's pure PyTorch, so the step count is what you control.

**🎚️ "Set active" now actually sets your agent's voice**
Previously it only picked the OmniVoice voice; Hermes kept speaking with whatever `tts.provider` said, so your clone worked in this plugin and nowhere else. It now writes `tts.provider: omnivoice` too — via a surgical one-line edit that leaves the rest of your `config.yaml`, comments included, untouched. The header shows which provider is *really* in use. Restart the gateway to apply it.

**Also:** the manifest declares `provides: tts`, so the provider shows up in the Settings voice-provider dropdown on newer Hermes builds. And two fixes went upstream to OmniVoice Studio itself — [macOS microphone entitlements](https://github.com/debpalash/OmniVoice-Studio/pull/1016) (merged: live recording never prompted for mic access because Hardened Runtime blocks it without the entitlement) and the CSM `ref_text` crash that made voice cloning impossible on that engine.

**Install / update — one command:**
```
hermes plugins install MahdiHedhli/hermes-omnivoice/omnivoice
hermes gateway restart
```

68 offline tests, live-verified on Hermes v0.18. Repo + full guide 👉 <https://github.com/MahdiHedhli/hermes-omnivoice>

Feedback and issues welcome 🙏
