# Contributing to Resonance Audio SDK

Thank you for your interest in contributing to Resonance!

---

## Quick Context: What is Resonance?

Before contributing, understand the scope.

**Resonance IS:**

- Runtime audio engine (plays sounds in real-time)
- Spatial audio with HRTF, voice management, DSP effects
- Cross-platform C API + language wrappers
- Genre-agnostic foundation for any game

**Resonance IS NOT:**

- Audio authoring tool (use DAWs)
- Dialogue, music composition, or visual editor
- Genre-specific middleware
- High-level "do everything" system

**You build:** weapon systems, dialogue, music, and ambient managers on top of Resonance.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the detailed design philosophy and [docs/RESONANCE.md](docs/RESONANCE.md) for the production-facing SDK overview.

---

## How this repo uses Resonance

This repository is the **Game Audio Engineering Kit**. Resonance is the proposed runtime foundation under [Preliminary Framework](README.md#preliminary-framework). Game-specific systems (weapons, dialogue, music, ambient, broadcast) stay in this kit and call Resonance rather than living inside it.

## Ground rules

1. Keep Resonance **runtime-only**. Do not add DAW, authoring UI, or asset-library features to the SDK surface.
2. Preserve a **minimal, stable C API**. Language wrappers wrap that API; they do not invent a second contract.
3. Prefer performance budgets already stated in the framework: voice allocation under 0.5 ms, DSP under 1 ms per frame.
4. Game-genre logic belongs in this kit (or a game project), not in Resonance.
5. Interactive gameplay audio and broadcast/show audio stay on separate pipelines. Shared contracts live in `data/events.json` and `integration/fmod/fmod_events.json`.

## Suggested workflow

1. Open an issue describing the change and which layer it belongs to (Resonance runtime vs kit-level game system).
2. Keep PRs small and scoped to one concern.
3. Update docs in the same PR when you change public behavior.
4. Run the existing kit tests:

```bash
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
```

## Where to put work

| Kind of change | Location |
| --- | --- |
| Resonance scope / philosophy | `docs/RESONANCE.md`, `docs/ARCHITECTURE.md` |
| Kit architecture, buses, mixer | `docs/ARCHITECTURE.md`, `engine/` |
| Engine plugins | `integration/`, `engine_integrations/` |
| Event contract | `data/events.json`, `integration/fmod/fmod_events.json` |
| Broadcast mix | `broadcast/` |
| Regression tests | `tests/` |
