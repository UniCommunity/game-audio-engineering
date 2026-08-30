# Game Audio Engineering Kit

Sound engineering stack for game development:

1. **Audio Engine** — mixing, spatialization, dynamic soundscapes
2. **Dynamic Mixer** — player-action priority, environment scaling, arena crowd, adaptive EQ
3. **Integration Layer** — Unity + Unreal plugins that post *events*, not files
4. **Broadcast Layer** — separate esports mix (commentary + crowd + ducked game)
5. **Testing Suite** — latency, clarity, positional accuracy, dynamic-mix contracts

Docs:

- [docs/GDD.md](docs/GDD.md) — game design document (audio)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — module boundaries and bus graph
- [docs/DYNAMIC_MIXING.md](docs/DYNAMIC_MIXING.md) — adaptive mix design

## Layout

```
data/events.json              shared event catalogue (includes priority tags)
engine/audio_engine.py        reference mixer + spatializer
engine/dynamic_mixer.py       action / environment / crowd / EQ controller
broadcast/broadcast_mixer.py  stream stem
integration/unity/            C# AudioApi + bridge
integration/unreal/           AudioEventSubsystem
tests/test_audio.py           latency / spatial / broadcast
tests/test_dynamic_mix.py     dynamic mixing contracts
```

The Python engine is a **reference implementation** so the contract can run and be tested without Unity/Unreal. Production games keep the same event ids and swap the renderer for native mixer, FMOD, or Wwise.

## Run tests

```bash
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
```

## Gameplay usage

```csharp
AudioApi.Post("sfx.footstep", pieceTransform);
AudioApi.SetRtpc("intensity", 0.7f);
AudioApi.IngestCrowdMic(0.55f);
AudioApi.SetDevice("headset");
AudioApi.SetSnapshot("arena_hot");
```

```cpp
UAudioEventSubsystem::PostAudioEvent(this, "sfx.footstep", Options);
```

```python
from engine.audio_engine import AudioEngine, Vec3
eng = AudioEngine(device="headset")
eng.set_rtpc("intensity", 0.7)
eng.ingest_crowd_mic(0.55)
eng.post("sfx.footstep", Vec3(2, 0, 1))
left, right, stems = eng.render_block()
print(eng.dynamic.last_report)
```

## Dynamic mixing (short)

- **Player-action sensitivity** — footsteps, gunfire, spells, reloads raise `action_heat` and get a priority boost so they are not masked.
- **Environmental adaptation** — rain / wind / hall beds scale down as scene intensity and heat rise.
- **Esports crowd** — live mic RMS balances crowd vs game with a 0.45 game-gain floor.
- **Priority layering** — `critical` voices are steal-protected and lifted against loud beds.
- **Real-time EQ** — headset vs PA vs laptop presets plus sidechain compression on beds.

Details: [docs/DYNAMIC_MIXING.md](docs/DYNAMIC_MIXING.md)

## Broadcast

`mix_broadcast(stems)` sidechains game + crowd to commentary and reports `clarity_db`.
Send that stereo stem to OBS/vMix; do not reuse the player master.

Repo: https://github.com/UniCommunity/game-audio-engineering
