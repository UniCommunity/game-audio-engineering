// EchoForge Adaptive Mixing Engine — Unity runtime hook.
// Analyses a live arena / spectator mic, gates residual noise, and
// rebalances ambient beds vs tagged priority cues (footsteps, gunfire,
// reload, spells). Talks to AudioKit.AudioApi so the same event contract
// used by the Python reference mixer stays in sync.
//
// Drop this on a persistent scene object. Assign:
//   - gameAudioSource  : master / ambience bus you want to duck
//   - crowdMicInput    : AudioSource fed by a Microphone.Start clip
//   - ambientSources   : weather, hall, crowd-bed loops
// Tag competitive AudioSources "PriorityCue" or register them in the inspector.
using System.Collections.Generic;
using UnityEngine;
using AudioKit;

namespace EchoForge
{
    [DisallowMultipleComponent]
    public class EchoForgeAudioEngine : MonoBehaviour
    {
        [Header("Buses")]
        public AudioSource gameAudioSource;
        public AudioSource crowdMicInput;
        public List<AudioSource> ambientSources = new List<AudioSource>();
        public List<AudioSource> prioritySources = new List<AudioSource>();

        [Header("Crowd analysis")]
        [Tooltip("RMS below this is treated as residual noise, not a crowd.")]
        [Range(0.01f, 0.6f)] public float noiseThreshold = 0.2f;
        [Tooltip("Hysteresis so the gate does not chatter around the threshold.")]
        [Range(0.0f, 0.2f)] public float noiseHysteresis = 0.04f;
        [Range(0.05f, 0.9f)] public float rmsAttack = 0.35f;
        [Range(0.01f, 0.4f)] public float rmsRelease = 0.08f;
        public int fftOrWindowSize = 256;

        [Header("Adaptive mix")]
        [Range(0.05f, 8f)] public float mixAdjustSpeed = 0.5f;
        [Range(0.2f, 1f)] public float gameGainFloor = 0.3f;
        [Range(0.5f, 1.5f)] public float priorityBoost = 1.0f;
        [Range(0f, 1f)] public float intensityInfluence = 0.45f;

        [Header("EchoForge / AudioApi bridge")]
        public string devicePreset = "headset";
        public bool pushCrowdToAudioApi = true;

        float _crowdRms;
        float _crowdLevel;
        float _cheer;
        float _targetVolume = 1f;
        float[] _scratch;
        bool _gateOpen;

        void Awake()
        {
            _scratch = new float[Mathf.Max(64, fftOrWindowSize)];
            if (string.IsNullOrEmpty(devicePreset) == false)
                AudioApi.SetDevice(devicePreset);
        }

        void Start()
        {
            if (prioritySources.Count == 0)
            {
                foreach (var src in FindObjectsOfType<AudioSource>())
                {
                    if (src != null && src.CompareTag("PriorityCue"))
                        prioritySources.Add(src);
                }
            }
        }

        void Update()
        {
            float instant = GetCrowdNoiseLevel();
            SmoothCrowd(instant);

            AdjustGameMix(_crowdLevel);
            ApplyNoiseCancellation(_crowdLevel);

            if (pushCrowdToAudioApi)
            {
                AudioApi.IngestCrowdMic(_crowdLevel);
                float intensity = Mathf.Clamp01(_crowdLevel * 0.7f + _cheer * 0.3f);
                AudioApi.SetRtpc("intensity", intensity);
            }
        }

        public float GetCrowdNoiseLevel()
        {
            if (crowdMicInput == null || crowdMicInput.clip == null)
                return 0f;

            int n = _scratch.Length;
            crowdMicInput.GetOutputData(_scratch, 0);
            float sum = 0f;
            for (int i = 0; i < n; i++)
                sum += _scratch[i] * _scratch[i];
            return Mathf.Sqrt(sum / n);
        }

        void SmoothCrowd(float instant)
        {
            float coeff = instant > _crowdRms ? rmsAttack : rmsRelease;
            _crowdRms = Mathf.Lerp(_crowdRms, instant, coeff);
            _crowdLevel = Mathf.Clamp01(_crowdRms * 1.4f);
            float transient = Mathf.Max(0f, instant - _crowdRms);
            _cheer = Mathf.Clamp01(_cheer * 0.85f + transient * 4f);
        }

        public void AdjustGameMix(float crowdLevel)
        {
            float desired = 1f - crowdLevel * (1f - gameGainFloor);
            desired = Mathf.Clamp(desired, gameGainFloor, 1f);
            _targetVolume = Mathf.Lerp(_targetVolume, desired, mixAdjustSpeed * Time.deltaTime);

            if (gameAudioSource != null)
                gameAudioSource.volume = _targetVolume;

            float ambGain = Mathf.Lerp(1f, 0.18f, crowdLevel * (0.55f + intensityInfluence));
            for (int i = 0; i < ambientSources.Count; i++)
            {
                var src = ambientSources[i];
                if (src == null) continue;
                src.volume = Mathf.Lerp(src.volume, ambGain, mixAdjustSpeed * Time.deltaTime);
            }

            float cueTarget = Mathf.Lerp(0.85f, priorityBoost, crowdLevel);
            for (int i = 0; i < prioritySources.Count; i++)
            {
                var src = prioritySources[i];
                if (src == null) continue;
                src.volume = Mathf.Lerp(src.volume, cueTarget, mixAdjustSpeed * Time.deltaTime);
            }
        }

        public void ApplyNoiseCancellation(float crowdLevel)
        {
            if (crowdMicInput == null) return;

            if (_gateOpen)
            {
                if (crowdLevel < noiseThreshold)
                    _gateOpen = false;
            }
            else
            {
                if (crowdLevel > noiseThreshold + noiseHysteresis)
                    _gateOpen = true;
            }

            crowdMicInput.mute = !_gateOpen;
        }

        public float CrowdLevel => _crowdLevel;
        public float CrowdCheer => _cheer;
        public bool CrowdGateOpen => _gateOpen;
    }
}
