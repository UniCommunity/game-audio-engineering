# FMOD Adaptive Mixing — games and esports

Sound designers author adaptive behaviour in **FMOD Studio**. Programmers only post events and set parameters. The shared catalogue in `data/events.json` is the contract; FMOD is one renderer of that contract.

Unity hook: [`integration/fmod/unity/FmodAudioManager.cs`](../integration/fmod/unity/FmodAudioManager.cs)
Unreal hook: [`integration/fmod/unreal/FmodAudioSubsystem.h`](../integration/fmod/unreal/FmodAudioSubsystem.h)
Path map: [`integration/fmod/fmod_events.json`](../integration/fmod/fmod_events.json)

Official plugins: FMOD for Unity, FMOD for Unreal.

## 1. Create Events for gameplay elements

In FMOD Studio, one Event per catalogue id. Route each Event to the matching bus.

| Catalogue id | FMOD path | Bus | Notes |
|---|---|---|---|
| `sfx.gunfire` | `event:/sfx/gunfire` | SFX | 3D, high priority |
| `sfx.footstep` | `event:/sfx/footstep` | SFX | 3D, critical, short |
| `sfx.reload` | `event:/sfx/reload` | SFX | critical |
| `sfx.spell.cast` | `event:/sfx/spell/cast` | SFX | high |
| `crowd.live` | `event:/crowd/live` | Crowd | looping bed |
| `crowd.cheer` | `event:/crowd/cheer` | Crowd | one-shot burst |
| `broadcast.comment.play` | `event:/broadcast/comment/play` | Commentary | ducks game via snapshot / sidechain |
| `vo.announce.check` | `event:/vo/announce/check` | Dialogue | |
| `music.state.explore` | `event:/music/state/explore` | Music | looping; tempo + density automated on `intensity` |
| `ambience.hall` / `rain` / `wind` | `event:/ambience/...` | Ambience | looping beds |

Event naming stays `domain/object/action` so Unity/Unreal/Python share one id.

## 2. Define Parameters from live game data

Create these as **global** FMOD parameters (so any Event or snapshot can read them):

| Parameter | Range | Driven by |
|---|---|---|
| `intensity` | 0–1 | match state, EchoForge crowd+cheer, or designer RTPC |
| `crowd_volume` | 0–1 | live arena mic RMS (`IngestCrowdMic`) |
| `player_health` | 0–1 | pawn health / respawn |
| `commentary_active` | 0 or 1 | broadcast VO gate |

Local parameters stay on a single Event (surface type on footsteps, weapon id on gunfire).

## 3. Link parameters to audio behaviour

Author this *in Studio*, not in C++/C#:

- **Music** — automate tempo, layer stems, or instrument mute against `intensity`. At 0.0 a pad; at 1.0 percussion + faster timeline tempo.
- **Ambience** — volume curve down as `intensity` or `crowd_volume` rises (floor ≈ −15 dB, never mute).
- **Crowd** — `crowd_volume` rides the Crowd bus. A sidechain compressor on Commentary / Dialogue uses Crowd as the detector, or a snapshot does the duck.
- **Commentary duck** — when `commentary_active` = 1, snapshot `broadcast_focus` pulls Music −8 dB and SFX −4 dB (same numbers as `data/events.json`).
- **Health** — low `player_health` can low-pass SFX or introduce a heartbeat Event; keep it a curve the designer owns.
- **DSP** — multiband EQ and compressor live on the Mixer buses. Snapshots (`normal`, `arena_hot`, `broadcast_focus`, `victory`, `check`) override those DSP knobs. Starting a snapshot Event is how the game applies a mix.

Programmers never set raw bus dB. They set `intensity` / `crowd_volume` / snapshot name.

## 4. Implement the FMOD engine in the game

### Unity

1. Install **FMOD for Unity**. Assign the built banks in FMOD Edit Settings.
2. Put `FmodAudioManager` on a bootstrap object.
3. `Awake` calls `InitializeFmod()`: load `Master` + `Master.strings`, start looping beds, cache snapshots.

```csharp
void Start()
{
    FmodAudioManager.Instance.InitializeFmod();
}

void OnMatchIntensity(float t)
{
    FmodAudioManager.Instance.SetIntensity(t);
}

void OnArenaMic(float rms)
{
    FmodAudioManager.Instance.IngestCrowdMic(rms);
}

void OnFire(Transform muzzle)
{
    FmodAudioManager.Instance.Post("sfx.gunfire", muzzle);
}

void OnCasterTalking(bool on)
{
    FmodAudioManager.Instance.SetCommentaryActive(on);
    if (on) FmodAudioManager.Instance.SetSnapshot("broadcast_focus");
}
```

`InitializeFmod` is the audio-manager entry point: banks load, Studio system is already created by `RuntimeManager`, beds and snapshots become live EventInstances.

### Unreal

Enable the FMOD Unreal plugin. `UFmodAudioSubsystem` wraps the Studio module and exposes Blueprint Post Audio Event, Set Intensity, Set Crowd Volume, Set Snapshot.

### Custom engine

Link `fmodstudio` + `fmod`. Load banks with `Studio::System::loadBankFile`, create instances with `getEvent("event:/sfx/gunfire")`, set globals with `setParameterByName`. Keep the same parameter and event names.

## Data flow

gameplay / EchoForge mic -> FmodAudioManager.SetParameter / Post / SetSnapshot -> FMOD Studio System (global params, snapshot instances, EventInstances) -> buses -> Master / Broadcast. Optionally mirror ids through AudioApi into the Python reference mixer.

Player mix and broadcast mix stay different Studio mixer sends. Do not reuse the player master for OBS.
