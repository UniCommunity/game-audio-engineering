# Resonance Audio SDK

**Production-grade runtime audio engine for game developers.**

Resonance delivers real-time spatial audio, DSP graph execution, and cross-platform voice management through a minimal, stable **C API**. It is a **genre-agnostic foundation** for building game-specific audio systems.

This page is the Resonance overview for the Game Audio Engineering Kit. The live landing section is [Preliminary Framework](../README.md#preliminary-framework).

---

## What is Resonance?

```
┌─────────────────────────────────────────────────────────────┐
│ RESONANCE AUDIO SDK                                         │
│                                                             │
│ IS:                         │ IS NOT:                       │
│ ✅ Runtime audio engine     │ ❌ Authoring tool (DAW)       │
│ ✅ Voice management         │ ❌ Dialogue system            │
│ ✅ DSP graph                │ ❌ Music composition          │
│ ✅ Spatial audio (HRTF)     │ ❌ Visual editor              │
│ ✅ Streaming I/O            │ ❌ Asset management           │
│ ✅ Cross-platform C API     │ ❌ High-level middleware      │
│ ✅ Genre-agnostic foundation│ ❌ Genre-specific tool        │
│ ✅ Performance-optimized    │ ❌ Feature-bloated            │
│                                                             │
│ YOU BUILD ON TOP:                                           │
│ Weapon systems, dialogue, music, ambient managers           │
│ Game-specific audio logic                                   │
└─────────────────────────────────────────────────────────────┘
```

**TL;DR:** Resonance is the **audio foundation** you call from your game code. You build game-specific systems (weapon audio, dialogue, music, ambient management) on top.

---

## Design Philosophy

### What Resonance IS (The Foundation)

- ✅ **Runtime audio engine** — Plays sounds in real-time during gameplay
- ✅ **Voice manager** — Allocates and prioritizes audio voices
- ✅ **DSP graph** — Real-time effect chains, filters, reverb, compression
- ✅ **Spatial audio** — 3D positioning with HRTF for realistic audio
- ✅ **Streaming I/O** — Efficient audio buffer and file management
- ✅ **Cross-platform** — Single codebase, all platforms (Windows, macOS, Linux, iOS, Android, consoles)
- ✅ **C API** — Minimal, stable interface with language-specific wrappers
- ✅ **Genre-agnostic** — Works for shooters, open-world, racing, VR, stealth, puzzle games
- ✅ **Performance-optimized** — <0.5ms voice allocation, <1ms DSP per frame

### What Resonance IS NOT (Excluded Scope)

- ❌ **Authoring tool** — Does not compose, arrange, or edit audio. Use DAWs (Reaper, Cubase, Logic)
- ❌ **Dialogue system** — Does not manage conversations or branching dialogue. Integrate external dialogue tools
- ❌ **Music composition** — Does not create musical scores. Hire composers or use existing tracks
- ❌ **Visual editor** — Does not have a drag-and-drop UI. Edit in your game engine
- ❌ **Asset management** — Does not organize audio files or metadata. Manage files yourself
- ❌ **Genre-specific middleware** — Not an "FPS audio engine" or "open-world audio engine". Build your own genre systems
- ❌ **High-level abstraction** — Not a black box. You control every detail
- ❌ **Feature-bloated** — Only includes what games need for real-time audio

### You Build On Top (Your Responsibility)

Games implement their own:

- **Weapon audio system** — Gunshot effects, impact sounds, gun type variations
- **Dialogue system** — NPC conversation management, branching dialogue
- **Music system** — Dynamic music transitions, state-based music changes
- **Ambient manager** — Handling 100+ simultaneous ambient sounds
- **Voice chat integration** — Spatial voice communication (using Vivox, Discord, etc.)
- **Game-specific audio logic** — How audio responds to game events

---

## Place in this kit

Resonance is the proposed runtime foundation under the kit's dual-pipeline architecture:

1. Interactive gameplay audio calls Resonance for voices, DSP, spatialization, and streaming I/O.
2. Broadcast / venue audio stays outside Resonance and consumes stems plus the shared event contract.
3. FMOD/Wwise remain authoring and middleware options. Resonance does not replace a DAW or a studio editor.

Related docs:

- [Architecture](ARCHITECTURE.md)
- [Contributing](../CONTRIBUTING.md)
- [Summary](SUMMARY.md)
