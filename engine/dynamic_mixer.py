"""Dynamic mixing: player-action priority, environment scaling, arena crowd, adaptive EQ."""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)

def lin_to_db(lin: float) -> float:
    return 20.0 * math.log10(max(lin, 1e-12))

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x

PRIORITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "bed": 0,
}

@dataclass
class MixLayer:
    name: str
    bus: str
    priority: str = "medium"
    gain_db: float = 0.0
    duck_group: str = "game"
    eq_shelf_hz: float = 0.0
    eq_shelf_db: float = 0.0

@dataclass
class CrowdInput:
    level: float = 0.0
    rms: float = 0.0
    cheer: float = 0.0

    def ingest(self, sample_rms: float, attack: float = 0.35, release: float = 0.08) -> None:
        sample_rms = clamp(sample_rms, 0.0, 1.0)
        coeff = attack if sample_rms > self.rms else release
        self.rms = self.rms + (sample_rms - self.rms) * coeff
        self.level = clamp(self.rms * 1.4, 0.0, 1.0)
        transient = max(0.0, sample_rms - self.rms)
        self.cheer = clamp(self.cheer * 0.85 + transient * 4.0, 0.0, 1.0)

@dataclass
class AdaptiveEQ:
    low_db: float = 0.0
    mid_db: float = 0.0
    high_db: float = 0.0
    makeup_db: float = 0.0

    def for_device(self, device: str) -> "AdaptiveEQ":
        device = (device or "headset").lower()
        if device in ("headset", "headphones", "iem"):
            return AdaptiveEQ(low_db=-1.5, mid_db=1.5, high_db=2.0, makeup_db=0.5)
        if device in ("pa", "arena", "speakers"):
            return AdaptiveEQ(low_db=1.0, mid_db=0.0, high_db=-1.0, makeup_db=-1.0)
        if device in ("laptop", "tv"):
            return AdaptiveEQ(low_db=2.0, mid_db=1.0, high_db=0.5, makeup_db=0.0)
        return AdaptiveEQ()

    def gain_for_synth(self, synth: str) -> float:
        if synth in ("tick", "click", "sting"):
            return db_to_lin(self.high_db + self.makeup_db)
        if synth in ("voice", "wood"):
            return db_to_lin(self.mid_db + self.makeup_db)
        if synth in ("hit", "fanfare", "pad", "cheer"):
            return db_to_lin(self.low_db * 0.5 + self.mid_db * 0.5 + self.makeup_db)
        return db_to_lin(self.makeup_db)

class SidechainCompressor:
    def __init__(self, threshold: float = 0.08, ratio: float = 4.0, attack: float = 0.25, release: float = 0.08):
        self.threshold = threshold
        self.ratio = ratio
        self.attack = attack
        self.release = release
        self.gr = 1.0

    def process_gain(self, detector_rms: float) -> float:
        if detector_rms > self.threshold:
            over = detector_rms / self.threshold
            target = 1.0 / (1.0 + (over - 1.0) * (self.ratio - 1.0) / self.ratio)
        else:
            target = 1.0
        coeff = self.attack if target < self.gr else self.release
        self.gr = self.gr + (target - self.gr) * coeff
        return self.gr

class DynamicMixer:
    def __init__(self, device: str = "headset"):
        self.device = device
        self.eq = AdaptiveEQ().for_device(device)
        self.crowd = CrowdInput()
        self.scene_intensity = 0.0
        self.action_heat = 0.0
        self.comp_ambience = SidechainCompressor(threshold=0.05, ratio=3.5)
        self.comp_crowd = SidechainCompressor(threshold=0.07, ratio=2.5, attack=0.15, release=0.12)
        self.comp_music = SidechainCompressor(threshold=0.06, ratio=4.0)
        self._priority_hits: List[Tuple[str, float]] = []
        self.last_report: Dict[str, float] = {}

    def set_device(self, device: str) -> None:
        self.device = device
        self.eq = AdaptiveEQ().for_device(device)

    def set_scene_intensity(self, value: float) -> None:
        self.scene_intensity = clamp(value, 0.0, 1.0)

    def ingest_crowd_mic(self, rms: float) -> None:
        self.crowd.ingest(rms)

    def register_action(self, event: str, priority: str, weight: float = 1.0) -> None:
        rank = PRIORITY_RANK.get(priority, 2)
        self._priority_hits.append((event, rank * weight))
        heat = min(1.0, rank / 4.0 * weight)
        self.action_heat = clamp(self.action_heat * 0.82 + heat * 0.45, 0.0, 1.0)

    def tick_decay(self) -> None:
        self.action_heat *= 0.92
        self._priority_hits = self._priority_hits[-32:]

    def environment_scale(self) -> float:
        mask = 0.55 * self.scene_intensity + 0.45 * self.action_heat
        return clamp(1.0 - 0.72 * mask, 0.18, 1.0)

    def music_scale(self) -> float:
        mask = 0.40 * self.scene_intensity + 0.50 * self.action_heat
        return clamp(1.0 - 0.65 * mask, 0.22, 1.0)

    def crowd_game_balance(self) -> Tuple[float, float]:
        live = self.crowd.level
        cheer = self.crowd.cheer
        crowd_g = clamp(0.35 + 0.55 * live + 0.25 * cheer, 0.2, 1.15)
        game_g = clamp(1.0 - 0.35 * live - 0.15 * cheer, 0.45, 1.0)
        return crowd_g, game_g

    def priority_boost_db(self, priority: str) -> float:
        rank = PRIORITY_RANK.get(priority, 2)
        bed = 0.5 * self.scene_intensity + 0.5 * self.crowd.level
        if rank >= 4:
            return 2.0 + 4.0 * bed
        if rank == 3:
            return 1.0 + 2.0 * bed
        if rank <= 1:
            return -3.0 * bed
        return 0.0

    def mix_stems(self, stems, voice_meta=None):
        empty = ([0.0], [0.0])
        def take(name):
            pair = stems.get(name, empty)
            return list(pair[0]), list(pair[1])
        sfx_l, sfx_r = take("sfx")
        ui_l, ui_r = take("ui")
        dlg_l, dlg_r = take("dialogue")
        mus_l, mus_r = take("music")
        amb_l, amb_r = take("ambience")
        crd_l, crd_r = take("crowd")
        com_l, com_r = take("commentary")
        n = max(len(sfx_l), len(mus_l), len(amb_l), len(crd_l), len(com_l), len(ui_l), len(dlg_l), 1)
        def pad(l, r):
            if len(l) < n:
                l = l + [0.0] * (n - len(l))
                r = r + [0.0] * (n - len(r))
            return l[:n], r[:n]
        sfx_l, sfx_r = pad(sfx_l, sfx_r)
        ui_l, ui_r = pad(ui_l, ui_r)
        dlg_l, dlg_r = pad(dlg_l, dlg_r)
        mus_l, mus_r = pad(mus_l, mus_r)
        amb_l, amb_r = pad(amb_l, amb_r)
        crd_l, crd_r = pad(crd_l, crd_r)
        com_l, com_r = pad(com_l, com_r)
        def rms(l, r):
            acc = 0.0
            for a, b in zip(l, r):
                acc += a * a + b * b
            return math.sqrt(acc / (2 * max(len(l), 1)))
        cue_rms = rms(sfx_l, sfx_r) + rms(ui_l, ui_r) + rms(dlg_l, dlg_r)
        amb_g = self.environment_scale() * self.comp_ambience.process_gain(cue_rms)
        mus_g = self.music_scale() * self.comp_music.process_gain(cue_rms + rms(dlg_l, dlg_r))
        crowd_g, game_g = self.crowd_game_balance()
        crowd_g *= self.comp_crowd.process_gain(cue_rms)
        sfx_boost = db_to_lin(self.priority_boost_db("critical" if self.action_heat > 0.35 else "high"))
        eq_sfx = self.eq.gain_for_synth("tick")
        eq_amb = self.eq.gain_for_synth("noise")
        eq_mus = self.eq.gain_for_synth("pad")
        eq_crd = self.eq.gain_for_synth("cheer")
        eq_com = self.eq.gain_for_synth("voice")
        def scale(l, r, g):
            return [x * g for x in l], [x * g for x in r]
        sfx_l, sfx_r = scale(sfx_l, sfx_r, game_g * sfx_boost * eq_sfx)
        ui_l, ui_r = scale(ui_l, ui_r, game_g * eq_sfx)
        dlg_l, dlg_r = scale(dlg_l, dlg_r, eq_com)
        mus_l, mus_r = scale(mus_l, mus_r, mus_g * eq_mus)
        amb_l, amb_r = scale(amb_l, amb_r, amb_g * eq_amb)
        crd_l, crd_r = scale(crd_l, crd_r, crowd_g * eq_crd)
        com_l, com_r = scale(com_l, com_r, eq_com)
        out_l = [0.0] * n
        out_r = [0.0] * n
        for pair in ((sfx_l, sfx_r), (ui_l, ui_r), (dlg_l, dlg_r), (mus_l, mus_r), (amb_l, amb_r), (crd_l, crd_r), (com_l, com_r)):
            for i in range(n):
                out_l[i] += pair[0][i]
                out_r[i] += pair[1][i]
        peak = max(1e-9, max(abs(x) for x in out_l + out_r))
        if peak > 0.99:
            s = 0.99 / peak
            out_l = [x * s for x in out_l]
            out_r = [x * s for x in out_r]
        self.last_report = {
            "scene_intensity": self.scene_intensity,
            "action_heat": self.action_heat,
            "crowd_level": self.crowd.level,
            "crowd_cheer": self.crowd.cheer,
            "ambience_gain": amb_g,
            "music_gain": mus_g,
            "crowd_gain": crowd_g,
            "game_gain": game_g,
            "sfx_boost": sfx_boost,
            "cue_rms": cue_rms,
            "device_high_db": self.eq.high_db,
            "peak": peak,
        }
        self.tick_decay()
        return out_l, out_r, self.last_report
