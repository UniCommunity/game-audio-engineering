// Unity integration — named events, not filenames.
using System;
using UnityEngine;

namespace AudioKit
{
    [Serializable]
    public class AudioEventOptions
    {
        public Vector3 position;
        public bool hasPosition;
        public float intensity = -1f;
    }

    public static class AudioApi
    {
        public static void Post(string eventId, Transform source = null)
        {
            var opt = new AudioEventOptions();
            if (source != null) { opt.position = source.position; opt.hasPosition = true; }
            AudioEventBridge.Instance?.Dispatch(eventId, opt);
        }
        public static void SetRtpc(string name, float value) => AudioEventBridge.Instance?.SetRtpc(name, value);
        public static void SetSnapshot(string name, float fadeMs = 50f) => AudioEventBridge.Instance?.SetSnapshot(name, fadeMs);
    }

    public class AudioEventBridge : MonoBehaviour
    {
        public static AudioEventBridge Instance { get; private set; }
        public TextAsset eventCatalog;
        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        public void Dispatch(string eventId, AudioEventOptions opt) { }
        public void SetRtpc(string name, float value) { }
        public void SetSnapshot(string name, float fadeMs) { }
    }
}
