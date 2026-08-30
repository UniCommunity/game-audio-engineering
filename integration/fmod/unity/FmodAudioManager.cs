// FMOD Studio adaptive mixer for games and esports broadcasts.
// Designers author events, parameters, snapshots and DSP in FMOD Studio.
// Gameplay only posts named events and drives global parameters.
// Requires the official FMOD for Unity package (FMODUnity).
using System.Collections.Generic;
using UnityEngine;
using FMOD.Studio;
using FMODUnity;
using AudioKit;

namespace EchoForge.FMOD
{
    public class FmodAudioManager : MonoBehaviour
    {
        public static FmodAudioManager Instance { get; private set; }

        [Header("Banks")]
        [BankRef] public string masterBank = "Master";
        [BankRef] public string stringsBank = "Master.strings";
        public bool loadSampleData = true;

        [Header("Persistent beds")]
        [EventRef] public string musicEvent = "event:/music/state/explore";
        [EventRef] public string ambienceEvent = "event:/ambience/hall";
        [EventRef] public string crowdLiveEvent = "event:/crowd/live";

        [Header("Snapshots (authored in FMOD Mixer)")]
        [EventRef] public string snapshotNormal = "snapshot:/normal";
        [EventRef] public string snapshotArenaHot = "snapshot:/arena_hot";
        [EventRef] public string snapshotBroadcastFocus = "snapshot:/broadcast_focus";
        [EventRef] public string snapshotVictory = "snapshot:/victory";

        [Header("Global parameters — match FMOD Studio names")]
        [ParamRef] public string intensityParam = "intensity";
        [ParamRef] public string crowdVolumeParam = "crowd_volume";
        [ParamRef] public string playerHealthParam = "player_health";
        [ParamRef] public string commentaryActiveParam = "commentary_active";

        EventInstance _music;
        EventInstance _ambience;
        EventInstance _crowd;
        EventInstance _activeSnapshot;
        readonly Dictionary<string, EventInstance> _snapshots = new Dictionary<string, EventInstance>();
        bool _ready;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeFmod();
        }

        public void InitializeFmod()
        {
            if (!string.IsNullOrEmpty(stringsBank))
                RuntimeManager.LoadBank(stringsBank, loadSampleData);
            if (!string.IsNullOrEmpty(masterBank))
                RuntimeManager.LoadBank(masterBank, loadSampleData);

            RuntimeManager.WaitForAllLoads();

            _music = StartBed(musicEvent);
            _ambience = StartBed(ambienceEvent);
            _crowd = StartBed(crowdLiveEvent);

            CacheSnapshot("normal", snapshotNormal);
            CacheSnapshot("arena_hot", snapshotArenaHot);
            CacheSnapshot("broadcast_focus", snapshotBroadcastFocus);
            CacheSnapshot("victory", snapshotVictory);
            SetSnapshot("normal");

            AudioApi.SetDevice("headset");
            _ready = true;
        }

        EventInstance StartBed(string path)
        {
            if (string.IsNullOrEmpty(path)) return default;
            var inst = RuntimeManager.CreateInstance(path);
            if (inst.isValid()) inst.start();
            return inst;
        }

        void CacheSnapshot(string name, string path)
        {
            if (string.IsNullOrEmpty(path)) return;
            var inst = RuntimeManager.CreateInstance(path);
            _snapshots[name] = inst;
        }

        void OnDestroy()
        {
            StopInstance(ref _music);
            StopInstance(ref _ambience);
            StopInstance(ref _crowd);
            foreach (var kv in _snapshots)
            {
                var inst = kv.Value;
                if (inst.isValid())
                {
                    inst.stop(STOP_MODE.IMMEDIATE);
                    inst.release();
                }
            }
            _snapshots.Clear();
        }

        static void StopInstance(ref EventInstance inst)
        {
            if (!inst.isValid()) return;
            inst.stop(STOP_MODE.ALLOWFADEOUT);
            inst.release();
            inst = default;
        }

        public void Post(string eventId, Transform source = null)
        {
            if (!_ready) return;
            string path = FmodEventMap.ToFmodPath(eventId);
            if (source != null)
                RuntimeManager.PlayOneShot(path, source.position);
            else
                RuntimeManager.PlayOneShot(path);
            AudioApi.Post(eventId, source);
        }

        public void SetParameter(string name, float value, bool ignoreSeekSpeed = false)
        {
            RuntimeManager.StudioSystem.setParameterByName(name, value, ignoreSeekSpeed);
            if (name == intensityParam) AudioApi.SetRtpc("intensity", value);
            if (name == crowdVolumeParam) AudioApi.IngestCrowdMic(value);
        }

        public void SetIntensity(float value) => SetParameter(intensityParam, Mathf.Clamp01(value));
        public void SetCrowdVolume(float value) => SetParameter(crowdVolumeParam, Mathf.Clamp01(value));
        public void SetPlayerHealth(float normalized) => SetParameter(playerHealthParam, Mathf.Clamp01(normalized));
        public void SetCommentaryActive(bool on) => SetParameter(commentaryActiveParam, on ? 1f : 0f);

        public void SetSnapshot(string name)
        {
            if (_activeSnapshot.isValid())
                _activeSnapshot.stop(STOP_MODE.ALLOWFADEOUT);
            if (_snapshots.TryGetValue(name, out var inst) && inst.isValid())
            {
                inst.start();
                _activeSnapshot = inst;
            }
            AudioApi.SetSnapshot(name);
        }

        public void IngestCrowdMic(float rms) => SetCrowdVolume(rms);
    }

    public static class FmodEventMap
    {
        static readonly Dictionary<string, string> Map = new Dictionary<string, string>
        {
            { "ui.click", "event:/ui/click" },
            { "ui.error", "event:/ui/error" },
            { "sfx.piece.select", "event:/sfx/piece/select" },
            { "sfx.piece.move", "event:/sfx/piece/move" },
            { "sfx.piece.capture", "event:/sfx/piece/capture" },
            { "sfx.check", "event:/sfx/check" },
            { "sfx.mate", "event:/sfx/mate" },
            { "sfx.footstep", "event:/sfx/footstep" },
            { "sfx.gunfire", "event:/sfx/gunfire" },
            { "sfx.reload", "event:/sfx/reload" },
            { "sfx.spell.cast", "event:/sfx/spell/cast" },
            { "vo.announce.check", "event:/vo/announce/check" },
            { "music.state.explore", "event:/music/state/explore" },
            { "ambience.hall", "event:/ambience/hall" },
            { "ambience.rain", "event:/ambience/rain" },
            { "ambience.wind", "event:/ambience/wind" },
            { "crowd.cheer", "event:/crowd/cheer" },
            { "crowd.live", "event:/crowd/live" },
            { "broadcast.comment.play", "event:/broadcast/comment/play" },
        };

        public static string ToFmodPath(string eventId)
        {
            if (string.IsNullOrEmpty(eventId)) return eventId;
            if (Map.TryGetValue(eventId, out var path)) return path;
            if (eventId.StartsWith("event:/") || eventId.StartsWith("snapshot:/")) return eventId;
            return "event:/" + eventId.Replace('.', '/');
        }
    }
}
