from pathlib import Path
from engine.mud_runtime import MudRuntime


def _runtime(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    cid = rt.create_character(world_id="shattered_realms", name="Phase Position")['character_id']
    rt.enter_world(cid, session_id="phase16g-position")
    return rt, cid


def _out(rt, cid, command):
    return rt.handle_input(cid, command)["output"]


def _pos(rt, cid):
    return (rt.active_characters[cid].actor_data or {}).get("position")


def test_position_commands_and_sleeping_look(tmp_path):
    rt, cid = _runtime(tmp_path)
    assert "You sit down and rest your tired bones." in _out(rt, cid, "rest")
    assert _pos(rt, cid) == "resting"
    assert "You need to stand up first." in _out(rt, cid, "north")
    assert _pos(rt, cid) == "resting"
    assert "You go to sleep." in _out(rt, cid, "sleep")
    assert _pos(rt, cid) == "sleeping"
    look = _out(rt, cid, "look")
    assert "In your dreams, or what?" in look
    assert "Exits:" not in look
    assert "Guildhall" not in look
    assert "You are asleep." in _out(rt, cid, "north")
    assert _pos(rt, cid) == "sleeping"
    assert "You wake and stand up." in _out(rt, cid, "wake")
    assert _pos(rt, cid) == "standing"
    assert "You lie down and go to sleep." in _out(rt, cid, "sleep")
    assert _pos(rt, cid) == "sleeping"


def test_runtime_tick_regenerates_without_input_and_clamps(tmp_path):
    rt, cid = _runtime(tmp_path)
    ch = rt.active_characters[cid]
    actor = rt.combat_runtime._resident_character_actor(ch)
    actor.resources.health = max(1, actor.resources.maximum_health - 10)
    actor.resources.mana = max(0, actor.resources.maximum_mana - 10)
    actor.resources.stamina = max(0, actor.resources.maximum_stamina - 10)
    rt.pulse_config["point_update_pulse_count"] = 1
    rt.runtime_resources._next_regeneration_monotonic = 0
    before = actor.resources.health
    processed = rt.runtime_resources.process_due_regeneration(10**6)
    assert processed >= 1
    assert actor.resources.health > before
    assert actor.resources.health <= actor.resources.maximum_health
    standing_gain = actor.resources.health - before
    _out(rt, cid, "rest")
    actor.resources.health = max(1, actor.resources.maximum_health - 10)
    rt.runtime_resources._next_regeneration_monotonic = 0
    before = actor.resources.health
    rt.runtime_resources.process_due_regeneration(10**6 + 1000)
    resting_gain = actor.resources.health - before
    assert resting_gain >= standing_gain
