## FMOD Studio adaptive mixer for Godot 4 (games + esports).
## Autoload as "FmodAudio". Supports FMODRuntime / FMODStudioModule and utopia-rise Fmod.
extends Node

@export var master_bank_path: String = "res://audio/Master.bank"
@export var strings_bank_path: String = "res://audio/Master.strings.bank"
@export var live_update: bool = true
@export var max_channels: int = 1024
@export var music_event: String = "event:/music/state/explore"
@export var ambience_event: String = "event:/ambience/hall"
@export var crowd_live_event: String = "event:/crowd/live"
@export var snapshot_normal: String = "snapshot:/normal"
@export var snapshot_combat: String = "snapshot:/arena_hot"
@export var snapshot_crowd: String = "snapshot:/arena_hot"
@export var snapshot_commentary: String = "snapshot:/broadcast_focus"
@export var snapshot_victory: String = "snapshot:/victory"

var _music
var _ambience
var _crowd
var _active_snapshot
var _snapshots := {}
var _ready_fmod := false
var _current_snapshot := "normal"

func _ready() -> void:
	initialize_fmod()

func _process(_delta: float) -> void:
	if has_node("/root/Fmod"):
		get_node("/root/Fmod").system_update()

func initialize_fmod() -> void:
	_init_studio_system()
	_load_bank(strings_bank_path)
	_load_bank(master_bank_path)
	_music = _start_bed(music_event)
	_ambience = _start_bed(ambience_event)
	_crowd = _start_bed(crowd_live_event)
	_cache_snapshot("normal", snapshot_normal)
	_cache_snapshot("combat", snapshot_combat)
	_cache_snapshot("crowd", snapshot_crowd)
	_cache_snapshot("commentary", snapshot_commentary)
	_cache_snapshot("arena_hot", snapshot_combat)
	_cache_snapshot("broadcast_focus", snapshot_commentary)
	_cache_snapshot("victory", snapshot_victory)
	set_snapshot("normal")
	_ready_fmod = true

func _init_studio_system() -> void:
	if Engine.has_singleton("Fmod"):
		var flags = 0x01 if live_update else 0
		Engine.get_singleton("Fmod").system_init(max_channels, flags, 0)

func _load_bank(path: String) -> void:
	if path.is_empty():
		return
	if Engine.has_singleton("Fmod"):
		Engine.get_singleton("Fmod").bank_load(path, 0)

func _start_bed(path: String):
	if path.is_empty():
		return null
	var inst = _create(path)
	if inst != null:
		inst.start()
	return inst

func _cache_snapshot(name: String, path: String) -> void:
	if path.is_empty():
		return
	_snapshots[name] = _create(path)

func _create(path: String):
	if typeof(FMODRuntime) != TYPE_NIL:
		return FMODRuntime.create_instance_path(path)
	if Engine.has_singleton("Fmod"):
		return Engine.get_singleton("Fmod").create_event_instance(path)
	push_warning("FMOD runtime not found; stub for %s" % path)
	return null

func _studio():
	if Engine.has_singleton("FMODStudioModule"):
		return FMODStudioModule.get_studio_system()
	if Engine.has_singleton("Fmod"):
		return Engine.get_singleton("Fmod")
	return null

func post(event_id: String, at: Node = null) -> void:
	if not _ready_fmod:
		return
	var path := FmodEventMap.to_fmod_path(event_id)
	if at != null and Engine.has_singleton("Fmod"):
		Engine.get_singleton("Fmod").play_one_shot(path, at)
		return
	if typeof(FMODRuntime) != TYPE_NIL:
		if at != null and at is Node3D:
			FMODRuntime.play_one_shot_attached_path(path, at)
		else:
			FMODRuntime.play_one_shot_path(path)

func set_parameter(name: String, value: float, ignore_seek: bool = false) -> void:
	var sys = _studio()
	if sys == null:
		return
	if sys.has_method("set_parameter_by_name"):
		sys.set_parameter_by_name(name, value, ignore_seek)
	elif sys.has_method("set_global_parameter_by_name"):
		sys.set_global_parameter_by_name(name, value)

func set_intensity(value: float) -> void:
	set_parameter("intensity", clampf(value, 0.0, 1.0))

func set_crowd_volume(value: float) -> void:
	set_parameter("crowd_volume", clampf(value, 0.0, 1.0))

func set_player_health(normalized: float) -> void:
	set_parameter("player_health", clampf(normalized, 0.0, 1.0))

func set_commentary_active(on: bool) -> void:
	set_parameter("commentary_active", 1.0 if on else 0.0)
	if on:
		set_snapshot("commentary")

func ingest_crowd_mic(rms: float) -> void:
	set_crowd_volume(rms)

func set_snapshot(name: String) -> void:
	if _active_snapshot != null and _active_snapshot.has_method("stop"):
		_active_snapshot.stop(0)
	if _snapshots.has(name) and _snapshots[name] != null:
		_snapshots[name].start()
		_active_snapshot = _snapshots[name]
		_current_snapshot = name

func mix_combat() -> void:
	set_snapshot("combat")
	set_intensity(0.85)

func mix_crowd() -> void:
	set_snapshot("crowd")

func mix_commentary() -> void:
	set_commentary_active(true)

func current_snapshot() -> String:
	return _current_snapshot
