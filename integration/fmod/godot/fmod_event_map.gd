class_name FmodEventMap
extends RefCounted

const MAP := {
	"ui.click": "event:/ui/click",
	"ui.error": "event:/ui/error",
	"sfx.piece.select": "event:/sfx/piece/select",
	"sfx.piece.move": "event:/sfx/piece/move",
	"sfx.piece.capture": "event:/sfx/piece/capture",
	"sfx.check": "event:/sfx/check",
	"sfx.mate": "event:/sfx/mate",
	"sfx.footstep": "event:/sfx/footstep",
	"sfx.gunfire": "event:/sfx/gunfire",
	"sfx.reload": "event:/sfx/reload",
	"sfx.spell.cast": "event:/sfx/spell/cast",
	"vo.announce.check": "event:/vo/announce/check",
	"music.state.explore": "event:/music/state/explore",
	"ambience.hall": "event:/ambience/hall",
	"ambience.rain": "event:/ambience/rain",
	"ambience.wind": "event:/ambience/wind",
	"crowd.cheer": "event:/crowd/cheer",
	"crowd.live": "event:/crowd/live",
	"broadcast.comment.play": "event:/broadcast/comment/play",
}


static func to_fmod_path(event_id: String) -> String:
	if MAP.has(event_id):
		return MAP[event_id]
	if event_id.begins_with("event:/") or event_id.begins_with("snapshot:/"):
		return event_id
	return "event:/" + event_id.replace(".", "/")
