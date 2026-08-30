# Dynamic Mixing

Automatically adjusts game audio from **player actions**, **environment intensity**, and **esports arena crowd** so competitive cues stay readable.

Repo: https://github.com/UniCommunity/game-audio-engineering

## Why this exists

A static bus mix fails in two places at once:

1. In-game: rain, music, and ability spam bury footsteps and reloads.
2. In-arena: a live crowd and PA fight the player / broadcast mix.

Dynamic mixing treats those as one control problem. Every block (256 samples @ 48 kHz) the mixer recomputes gains from tagged events, scene RTPCs, and a live microphone envelope.

## Pillars

### 1. Player-action sensitivity

The engine watches posted events (`sfx.footstep`, `sfx.gunfire`, `sfx.spell.cast`, `sfx.reload`). Each catalogue entry carries a `priority`:

| tag | examples | behaviour |
|---|---|---|
| `critical` | footsteps, reload, commentary | lifted when beds get loud; voices are steal-protected |
| `high` | gunfire, spell cast, check sting | modest lift + feeds action-heat |
| `medium` | UI, generic SFX | follow game gain |
| `low` / `bed` | rain, wind, hall, music | first to duck |

`action_heat` is a one-pole envelope of recent high-rank posts. It decays ~8% per block so a burst of footsteps keeps the bed down for a few hundred milliseconds after the last step.

### 2. Environmental adaptation

`SetRtpc("intensity", 0..1)` and `set_scene_intensity` drive ambience and music:

```
ambience_gain = clamp(1 - 0.72 * (0.55*intensity + 0.45*heat), 0.18, 1.0)
music_gain    = clamp(1 - 0.65 * (0.40*intensity + 0.50*heat), 0.22, 1.0)
```

Wind / rain / crowd chatter scale with the scene instead of sitting at a fixed loop level. Immersion remains; masking does not.

### 3. Esports crowd integration

`ingest_crowd_mic(rms)` accepts a 0–1 envelope from arena mics (or a simulated cheer bus). Attack is faster than release so a roar punches through, then settles.

Balance:

```
crowd_gain = 0.35 + 0.55*level + 0.25*cheer
game_gain  = 1.00 - 0.35*level - 0.15*cheer   # floor 0.45
```

Players never lose the floor under their footsteps. Spectators still feel the room. Broadcast continues to sidechain both to commentary (`broadcast/broadcast_mixer.py`).

### 4. Priority layering

Critical voices are marked `protect=True` on the dialogue / commentary buses **and** receive a broadband boost:

```
boost_db = 2 + 4 * bed_loudness    # critical
boost_db = 1 + 2 * bed_loudness    # high
```

Voice stealing still prefers unprotected, oldest voices. Reloads and footsteps survive a 32-voice cap better than UI ticks.

### 5. Real-time equalization + compression

`AdaptiveEQ.for_device(device)` tilts three bands:

- headset / IEM: slight low cut, mid/high lift (cue speech band)
- arena PA: low lift, high cut (less harsh on a system already bright)
- laptop / TV: low and mid lift

A sidechain compressor on ambience, music, and crowd uses cue RMS (SFX + UI + dialogue) as the detector. Thresholds are deliberately high so quiet exploration is not pumped.

## Runtime contract

```python
from engine.audio_engine import AudioEngine, Vec3

eng = AudioEngine(device="headset")
eng.set_rtpc("intensity", 0.7)
eng.ingest_crowd_mic(0.55)
eng.post("sfx.footstep", Vec3(2, 0, 1))
left, right, stems = eng.render_block()
report = eng.dynamic.last_report
```

Unity:

```csharp
AudioApi.SetRtpc("intensity", 0.7f);
AudioApi.IngestCrowdMic(0.55f);
AudioApi.SetDevice("headset");
AudioApi.Post("sfx.footstep", playerTransform);
```

## Mapping to middleware

Keep the same event ids. In Wwise / FMOD:

- `priority` → playback priority + HDR / mixer snapshot
- `intensity` RTPC → music switch / ambience volume curve
- crowd mic RMS → RTPC on a Crowd bus with sidechain to SFX
- device EQ → output bus effect preset (headset vs PA)

The Python engine is the contract and the test oracle, not the shipping renderer.

## Tests

`tests/test_dynamic_mix.py` checks:

- critical footsteps stay louder than rain when both play
- ambience drops as intensity rises
- crowd mic raises crowd stem without collapsing game below 0.45
- headset EQ boosts tick-class cues vs arena PA
- action heat decays after events stop
