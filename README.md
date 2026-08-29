# Game Audio Engineering Kit

Sound engineering stack for game development:

1. **Audio Engine** — mixing, spatialization, dynamic soundscapes  
2. **Integration Layer** — Unity + Unreal plugins that post *events*, not files  
3. **Broadcast Layer** — separate esports mix (commentary + crowd + ducked game)  
4. **Testing Suite** — latency, clarity, positional accuracy  

Docs:

- [docs/GDD.md](docs/GDD.md) — game design document (audio)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — module boundaries and bus graph

## Layout

```
data/events.json              shared event catalogue
engine/audio_engine.py        reference mixer + spatializer
broadcast/broadcast_mixer.py  stream stem
integration/unity/            C# AudioApi + bridge
integration/unreal/           AudioEventSubsystem
tests/test_audio.py           automated checks
```

The Python engine is a **reference implementation** so the contract can run and be tested without Unity/Unreal. Production games keep the same event ids and swap the renderer for native mixer, FMOD, or Wwise.

## Run tests

```bash
python3 tests/test_audio.py
```

## Gameplay usage

```csharp
AudioApi.Post("sfx.piece.capture", pieceTransform);
AudioApi.SetRtpc("intensity", 0.7f);
AudioApi.SetSnapshot("check");
```

```cpp
UAudioEventSubsystem::PostAudioEvent(this, "sfx.piece.capture", Options);
```

```python
from engine.audio_engine import AudioEngine, Vec3
eng = AudioEngine()
eng.post("sfx.piece.capture", Vec3(2, 0, 0))
left, right, stems = eng.render_block()
```

## Broadcast

`mix_broadcast(stems)` sidechains game + crowd to commentary and reports `clarity_db`.
Send that stereo stem to OBS/vMix; do not reuse the player master.

Repo: https://github.com/UniCommunity/game-audio-engineering
