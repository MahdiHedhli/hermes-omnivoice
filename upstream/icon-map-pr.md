# DRAFT — additive `ICON_MAP` PR for NousResearch/hermes-agent

**Status: OPENED as a draft PR (owner-authorized).**
PR: https://github.com/NousResearch/hermes-agent/pull/57764 — base `main`, +4/−0,
draft. Target repo: `NousResearch/hermes-agent`. A tracking issue can be linked
before flipping it to ready-for-review.

## Why

Dashboard plugin tabs pick their icon from a fixed Lucide `ICON_MAP` in
`web/src/App.tsx`. There is **no mic/waveform icon** in the map today, so a
voice/TTS plugin (e.g. the OmniVoice **Voices** tab) has to borrow
`MessageSquare` / `Zap` / `Sparkles`. This adds two voice-appropriate icons
(`AudioLines`, `Mic`) that already ship with `lucide-react`. Purely additive —
no existing entry changes, unknown names still fall back to `Puzzle`.

## Diff (against `web/src/App.tsx`; rebase on upstream `main` before submitting)

```diff
--- a/web/src/App.tsx
+++ b/web/src/App.tsx
@@ lucide-react import block
 import {
   Activity,
+  AudioLines,
   BarChart3,
   BookOpen,
@@ lucide-react import block (continued)
   Menu,
   MessageSquare,
+  Mic,
   Package,
@@ const ICON_MAP: Record<string, ComponentType<{ className?: string }>> = {
   Activity,
+  AudioLines,
   BarChart3,
   Clock,
@@ const ICON_MAP (continued)
   MessageSquare,
+  Mic,
   Package,
```

## PR title

`feat(dashboard): add AudioLines + Mic to plugin ICON_MAP`

## PR body

> Additive: registers `AudioLines` and `Mic` (both already in `lucide-react`) in
> the dashboard plugin `ICON_MAP` so voice/TTS plugin tabs can use a fitting
> icon instead of borrowing `MessageSquare`. No existing entries change; unknown
> icon names continue to fall back to `Puzzle` via `resolveIcon`. Motivated by
> the OmniVoice Voices tab (github.com/MahdiHedhli/hermes-omnivoice). Refs #XXXX.

## Follow-up in this plugin (after the PR merges upstream)

Once `AudioLines` is in a released Hermes `ICON_MAP`, switch
`omnivoice/dashboard/manifest.json` `"icon"` from `"MessageSquare"` to
`"AudioLines"`. Until then keep `MessageSquare` — an unmerged icon name would
fall back to `Puzzle` on current builds.
