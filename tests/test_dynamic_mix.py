"""Dynamic mixing acceptance checks."""
from __future__ import annotations
import math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine.audio_engine import AudioEngine, Vec3
from engine.dynamic_mixer import DynamicMixer


def _rms(l, r=None):
    if r is None:
        r = l
    return math.sqrt(sum(a * a + b * b for a, b in zip(l, r)) / (2 * max(len(l), 1)))


def test_footsteps_cut_through_rain():
    wet = AudioEngine()
    wet.set_rtpc("intensity", 0.9)
    wet.post("ambience.rain")
    wet.post("sfx.footstep", Vec3(1, 0, 0))
    dry = AudioEngine()
    dry.post("sfx.footstep", Vec3(1, 0, 0))
    wet_sfx = dry_sfx = 0.0
    for _ in range(12):
        _, _, stems_w = wet.render_block()
        _, _, stems_d = dry.render_block()
        wet_sfx += _rms(*stems_w["sfx"])
        dry_sfx += _rms(*stems_d["sfx"])
    assert wet.dynamic.last_report["ambience_gain"] < 0.55
    assert wet.dynamic.last_report["sfx_boost"] >= 1.0
    assert wet_sfx > 0.0 and dry_sfx > 0.0


def test_environment_scales_with_intensity():
    lo = DynamicMixer()
    lo.set_scene_intensity(0.1)
    hi = DynamicMixer()
    hi.set_scene_intensity(0.95)
    assert hi.environment_scale() < lo.environment_scale()
    assert hi.music_scale() < lo.music_scale()


def test_crowd_mic_keeps_game_floor():
    mx = DynamicMixer()
    mx.ingest_crowd_mic(0.9)
    mx.ingest_crowd_mic(0.9)
    crowd_g, game_g = mx.crowd_game_balance()
    assert crowd_g > 0.6
    assert game_g >= 0.45


def test_headset_eq_lifts_tick_more_than_pa():
    hs = DynamicMixer(device="headset")
    pa = DynamicMixer(device="pa")
    assert hs.eq.gain_for_synth("tick") > pa.eq.gain_for_synth("tick")


def test_action_heat_decays():
    eng = AudioEngine()
    for _ in range(6):
        eng.post("sfx.reload")
        eng.render_block()
    hot = eng.dynamic.action_heat
    for _ in range(40):
        eng.render_block()
    assert hot > 0.2
    assert eng.dynamic.action_heat < hot * 0.5


def test_critical_voice_survives_cap():
    eng = AudioEngine()
    eng.post("sfx.footstep")
    for _ in range(64):
        eng.post("ui.click")
    eng.render_block()
    alive = {v.event for v in eng.voices if v.alive}
    assert "sfx.footstep" in alive


if __name__ == "__main__":
    failed = 0
    for fn in [
        test_footsteps_cut_through_rain,
        test_environment_scales_with_intensity,
        test_crowd_mic_keeps_game_floor,
        test_headset_eq_lifts_tick_more_than_pa,
        test_action_heat_decays,
        test_critical_voice_survives_cap,
    ]:
        try:
            fn()
            print("PASS", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, e)
    raise SystemExit(failed)
