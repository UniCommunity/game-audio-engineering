"""Esports / stream mix: commentary on top, crowd present, game ducked."""
from __future__ import annotations
from typing import Dict, List, Tuple
from engine.audio_engine import db_to_lin

def _rms(l, r):
    if not l: return 0.0
    acc = 0.0
    for a, b in zip(l, r):
        acc += a * a + b * b
    return (acc / (2 * len(l))) ** 0.5

def _scale(l, r, g):
    return [x * g for x in l], [x * g for x in r]

def _sum(pairs):
    n = len(pairs[0][0])
    ol = [0.0] * n
    or_ = [0.0] * n
    for l, r in pairs:
        for i in range(n):
            ol[i] += l[i]
            or_[i] += r[i]
    return ol, or_

def mix_broadcast(stems, commentary_duck_db=-8.0, game_sfx_extra_db=-4.0):
    empty = ([0.0], [0.0])
    sfx = stems.get("sfx", empty)
    music = stems.get("music", empty)
    amb = stems.get("ambience", empty)
    ui = stems.get("ui", empty)
    crowd = stems.get("crowd", empty)
    comm = stems.get("commentary", empty)
    dialogue = stems.get("dialogue", empty)
    comm_rms = _rms(*comm) + _rms(*dialogue)
    duck = db_to_lin(commentary_duck_db) if comm_rms > 0.01 else 1.0
    sfx_g = db_to_lin(game_sfx_extra_db) * duck
    music_g = db_to_lin(-8.0) * duck
    game = _sum([_scale(*sfx, sfx_g), _scale(*music, music_g), _scale(*amb, duck), _scale(*ui, duck)])
    out = _sum([game, _scale(*crowd, duck), _sum([comm, dialogue])])
    peak = max(1e-9, max(abs(x) for x in out[0] + out[1]))
    if peak > 0.99:
        s = 0.99 / peak
        out = ([x * s for x in out[0]], [x * s for x in out[1]])
    import math
    metrics = {
        "commentary_rms": comm_rms,
        "sfx_rms": _rms(*sfx) * sfx_g,
        "clarity_db": 20.0 * math.log10((comm_rms + 1e-9) / (_rms(*sfx) * sfx_g + 1e-9)),
    }
    return out[0], out[1], metrics
