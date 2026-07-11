from tests.phase11b_helpers import svc

def test_phase11b_perception_foundation(tmp_path):
    p = svc(tmp_path)
    assert not p.validate_content()["errors"]
    hide = p.attempt_hide("actor_a", room_id="room_a")
    assert hide["status"] == "hidden"
    assert p.attempt_hide("actor_a", room_id="room_a")["duplicate"] is True
    det = p.evaluate_actor_detection("observer", "actor_a", room_id="room_a")
    assert det["result"] in {"not_detected", "hint", "partial", "silhouette", "detected", "identified"}
    trail = p.create_trail("footprint", "actor_a", "room_a", direction="north", event_id="move1")
    assert p.create_trail("footprint", "actor_a", "room_a", direction="north", event_id="move1")["trail_id"] == trail["trail_id"]
    assert p.find_tracks("observer", "room_a")
    assert "Tracks lead" in p.get_tracking_hint("observer", trail["trail_id"])["message"]
    assert p.track_target("observer", "tracks", room_id="room_a")["status"] == "tracking"
    p.create_trail("scent", "actor_a", "room_a", direction="north", event_id="scent1", strength=12)
    assert p.detect_scent("observer", "room_a")["result"] != "no_scent"
    sound = p.emit_sound("shout_sound", "room_a", source_actor_id="actor_a")
    assert p.hear_sound("observer", sound["sound_event_id"], distance=1, direction="east")["result"] != "inaudible"
    assert p.conceal_item("item_1", "actor_a", "room_a")["ok"]
    assert p.break_hide("actor_a", "combat")["status"] == "broken"
