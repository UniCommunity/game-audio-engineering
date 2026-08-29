"""Automated latency, clarity, and positional checks."""
from __future__ import annotations
import math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from broadcast.broadcast_mixer import mix_broadcast
from engine.audio_engine import AudioEngine, Vec3

def _rms_channel(ch):
    return math.sqrt(sum(x * x for x in ch) / max(len(ch), 1))

def test_latency_under_40ms():
    eng = AudioEngine()
    eng.post("ui.click")
    eng.render_block()
    assert eng.last_event_sample["ui.click"] == 0
    l, r, _ = eng.render_block()
    peak_i = max(range(len(l)), key=lambda i: abs(l[i]) + abs(r[i]))
    assert peak_i / eng.sr * 1000.0 < 40.0

def test_positional_right_is_louder_in_right():
    eng = AudioEngine()
    eng.post("sfx.piece.capture", Vec3(5, 0, 0))
    l, r = [], []
    for _ in range(20):
        bl, br, _ = eng.render_block(); l.extend(bl); r.extend(br)
    assert _rms_channel(r) > _rms_channel(l) * 1.15

def test_positional_left_is_louder_in_left():
    eng = AudioEngine()
    eng.post("sfx.piece.capture", Vec3(-5, 0, 0))
    l, r = [], []
    for _ in range(20):
        bl, br, _ = eng.render_block(); l.extend(bl); r.extend(br)
    assert _rms_channel(l) > _rms_channel(r) * 1.15

def test_broadcast_clarity_when_commentary_active():
    eng = AudioEngine()
    eng.post("sfx.piece.capture", Vec3(1, 0, 0))
    eng.post("broadcast.comment.play")
    for _ in range(9):
        _, _, stems = eng.render_block()
    _, _, metrics = mix_broadcast(stems)
    assert metrics["clarity_db"] >= 6.0, metrics

def test_voice_cap_does_not_steal_commentary():
    eng = AudioEngine()
    eng.post("broadcast.comment.play")
    for _ in range(64):
        eng.post("ui.click")
    eng.render_block()
    assert "broadcast.comment.play" in {v.event for v in eng.voices if v.alive}

def test_unknown_event_is_ignored():
    eng = AudioEngine()
    eng.post("does.not.exist")
    eng.render_block()
    assert eng.voices == []

if __name__ == "__main__":
    failed = 0
    for fn in [test_latency_under_40ms, test_positional_right_is_louder_in_right,
               test_positional_left_is_louder_in_left, test_broadcast_clarity_when_commentary_active,
               test_voice_cap_does_not_steal_commentary, test_unknown_event_is_ignored]:
        try:
            fn(); print("PASS", fn.__name__)
        except Exception as e:
            failed += 1; print("FAIL", fn.__name__, e)
    raise SystemExit(failed)
