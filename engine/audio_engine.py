"""Reference audio engine: events, voices, spatialization, buses, dynamic mix."""
from __future__ import annotations
import json, math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from engine.dynamic_mixer import DynamicMixer

SAMPLE_RATE, BLOCK, VOICE_CAP = 48000, 256, 32
SPEED_OF_SOUND, HEAD_RADIUS = 343.0, 0.09

def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

@dataclass
class Vec3:
    x: float = 0.0; y: float = 0.0; z: float = 0.0
    def sub(self, o): return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)
    def length(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)

@dataclass
class Listener:
    position: Vec3 = field(default_factory=Vec3)
    forward: Vec3 = field(default_factory=lambda: Vec3(0, 0, -1))
    up: Vec3 = field(default_factory=lambda: Vec3(0, 1, 0))

@dataclass
class Command:
    kind: str; event: str = ""; position: Optional[Vec3] = None
    rtpc: str = ""; value: float = 0.0; snapshot: str = ""; fade_ms: float = 50.0

class Synth:
    @staticmethod
    def render(kind, n, sr, t0):
        out = [0.0] * n
        for i in range(n):
            t = t0 + i / sr
            if kind == "click": out[i] = math.sin(2*math.pi*1800*t) * math.exp(-t*60)
            elif kind == "tick": out[i] = math.sin(2*math.pi*1200*t) * math.exp(-t*40)
            elif kind == "wood": out[i] = math.sin(2*math.pi*420*t) * math.exp(-t*18)
            elif kind == "hit": out[i] = (math.sin(2*math.pi*180*t)+0.4*math.sin(2*math.pi*90*t))*math.exp(-t*12)
            elif kind == "sting": out[i] = math.sin(2*math.pi*880*t)*math.exp(-t*8)
            elif kind == "fanfare": out[i] = 0.5*math.sin(2*math.pi*523*t)+0.3*math.sin(2*math.pi*659*t)
            elif kind == "voice":
                f = 160 + 40*math.sin(2*math.pi*3*t); out[i] = 0.35*math.sin(2*math.pi*f*t)
            elif kind == "pad": out[i] = 0.15*(math.sin(2*math.pi*220*t)+math.sin(2*math.pi*330*t))
            elif kind == "noise":
                x = math.sin(t*127.1)*43758.5453; out[i] = 0.04*(x-math.floor(x)-0.5)
            elif kind == "cheer":
                x = math.sin(t*91.7)*12345.67; nse = x-math.floor(x)-0.5
                out[i] = 0.2*nse*(0.5+0.5*math.sin(2*math.pi*2*t))
            elif kind == "error": out[i] = math.sin(2*math.pi*240*t)*math.exp(-t*10)
        return out

@dataclass
class Voice:
    event: str; bus: str; synth: str; gain: float; spatial: bool
    position: Vec3; loop: bool; t: float = 0.0; alive: bool = True; age: float = 0.0
    protect: bool = False; priority: str = "medium"
    def tick(self, n, sr):
        buf = Synth.render(self.synth, n, sr, self.t)
        self.t += n/sr; self.age += n/sr
        if not self.loop and self.age > 1.2: self.alive = False
        return [s*self.gain for s in buf]

class Spatializer:
    def __init__(self, dmin=1.0, dmax=30.0):
        self.dmin, self.dmax = dmin, dmax
    def process(self, mono, src, listener, sr):
        rel = src.sub(listener.position)
        dist = max(rel.length(), 0.001)
        att = 1.0 if dist <= self.dmin else clamp(self.dmin/dist, db_to_lin(-60), 1.0)
        az = math.atan2(rel.x, -rel.z)
        pan = clamp(math.sin(az), -1.0, 1.0)
        gl = math.sqrt((1.0-pan)*0.5)*att
        gr = math.sqrt((1.0+pan)*0.5)*att
        itd = (HEAD_RADIUS/SPEED_OF_SOUND)*math.sin(az)
        delay = int(round(abs(itd)*sr))
        left, right = [0.0]*len(mono), [0.0]*len(mono)
        for i,s in enumerate(mono):
            if itd >= 0:
                left[i] = s*gl
                if i+delay < len(mono): right[i+delay] += s*gr
                else: right[i] += s*gr*0.5
            else:
                right[i] = s*gr
                if i+delay < len(mono): left[i+delay] += s*gl
                else: left[i] += s*gl*0.5
        return left, right

class Bus:
    def __init__(self, name):
        self.name=name; self.gain_db=0.0; self.snapshot_db=0.0
        self.left=[0.0]*BLOCK; self.right=[0.0]*BLOCK
    def clear(self, n):
        self.left=[0.0]*n; self.right=[0.0]*n
    def mix_stereo(self, l, r):
        g = db_to_lin(self.gain_db + self.snapshot_db)
        for i in range(len(l)):
            self.left[i]+=l[i]*g; self.right[i]+=r[i]*g

class SoundscapeDirector:
    def __init__(self, engine):
        self.engine=engine; self.current=""; self.intensity=0.0
    def set_scape(self, name):
        self.current=name
        if name.endswith("opening") or name.endswith("calm"):
            self.engine.post("ambience.hall"); self.engine.post("music.state.explore")
        if "hot" in name:
            self.engine.set_rtpc("intensity", 0.85)
            self.engine.set_snapshot("arena_hot")
    def set_intensity(self, v):
        self.intensity=clamp(v,0,1); self.engine.set_rtpc("intensity", self.intensity)

class AudioEngine:
    def __init__(self, catalog_path=None, sr=SAMPLE_RATE, block=BLOCK, device="headset"):
        self.sr, self.block = sr, block
        path = catalog_path or str(Path(__file__).resolve().parents[1]/"data"/"events.json")
        self.catalog = json.loads(Path(path).read_text())
        self.listener=Listener(); self.spatial=Spatializer()
        self.voices=[]; self.queue=[]; self.rtpcs={"intensity":0.0}
        self.buses={n:Bus(n) for n in self.catalog["buses"]}
        self.snapshot="normal"; self.soundscape=SoundscapeDirector(self)
        self.frames_rendered=0; self.last_event_sample={}
        self.dynamic = DynamicMixer(device=device)
        self.apply_snapshot("normal", 0)
    def post(self, event, position=None):
        self.queue.append(Command("play", event=event, position=position or Vec3()))
    def set_rtpc(self, name, value):
        self.queue.append(Command("rtpc", rtpc=name, value=value))
    def set_snapshot(self, name, fade_ms=50.0):
        self.queue.append(Command("snapshot", snapshot=name, fade_ms=fade_ms))
    def set_listener(self, position, forward=None):
        self.listener.position=position
        if forward: self.listener.forward=forward
    def set_device(self, device):
        self.dynamic.set_device(device)
    def ingest_crowd_mic(self, rms):
        self.dynamic.ingest_crowd_mic(rms)
    def apply_snapshot(self, name, _fade):
        spec=self.catalog.get("snapshots",{}).get(name,{})
        self.snapshot=name
        for bus in self.buses.values():
            bus.snapshot_db=float(spec.get(bus.name,0.0))
    def _steal_if_needed(self):
        live=[v for v in self.voices if v.alive]
        if len(live)<int(self.catalog.get("voice_cap", VOICE_CAP)): return
        victims=[v for v in live if not v.protect]
        if victims:
            victims.sort(key=lambda v: (1 if v.priority == "critical" else 0, -v.age))
            victims[0].alive = False
    def _consume(self):
        while self.queue:
            cmd=self.queue.pop(0)
            if cmd.kind=="rtpc":
                self.rtpcs[cmd.rtpc]=cmd.value
                if cmd.rtpc=="intensity":
                    self.dynamic.set_scene_intensity(cmd.value)
            elif cmd.kind=="snapshot": self.apply_snapshot(cmd.snapshot, cmd.fade_ms)
            elif cmd.kind=="play":
                spec=self.catalog["events"].get(cmd.event)
                if not spec: continue
                self._steal_if_needed()
                priority = spec.get("priority", "medium")
                protect = spec["bus"] in ("dialogue","commentary") or priority=="critical"
                self.voices.append(Voice(cmd.event, spec["bus"], spec.get("synth","tick"),
                    db_to_lin(spec.get("gain_db",0.0)), bool(spec.get("spatial")),
                    cmd.position or Vec3(), bool(spec.get("loop")),
                    protect=protect, priority=priority))
                self.dynamic.register_action(cmd.event, priority)
                self.last_event_sample[cmd.event]=self.frames_rendered
    def render_block(self, apply_dynamic=True):
        self._consume(); n=self.block
        for b in self.buses.values(): b.clear(n)
        still=[]
        for v in self.voices:
            if not v.alive: continue
            mono=v.tick(n,self.sr)
            l,r = self.spatial.process(mono,v.position,self.listener,self.sr) if v.spatial else (mono,mono)
            self.buses[v.bus].mix_stereo(l,r)
            if v.alive: still.append(v)
        self.voices=still
        self.buses["music"].snapshot_db += -6.0*self.rtpcs.get("intensity",0.0)
        stems={}
        for name,bus in self.buses.items():
            if name=="master": continue
            stems[name]=(bus.left[:], bus.right[:])
        if apply_dynamic:
            ml, mr, _report = self.dynamic.mix_stems(stems)
        else:
            ml,mr=[0.0]*n,[0.0]*n
            for name,bus in self.buses.items():
                if name=="master": continue
                for i in range(n):
                    ml[i]+=bus.left[i]; mr[i]+=bus.right[i]
        peak=max(1e-9, max(abs(x) for x in ml+mr))
        if peak>0.99:
            s=0.99/peak; ml=[x*s for x in ml]; mr=[x*s for x in mr]
        self.buses["master"].left, self.buses["master"].right = ml, mr
        self.frames_rendered += n
        return ml, mr, stems
