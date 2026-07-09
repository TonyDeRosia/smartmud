from types import SimpleNamespace
from engine.mud_commands import MudCommandEngine
from smart_mud.event_bus import EventBus


def char(role="player"):
    return SimpleNamespace(id="c1", account_id="a1", name="Tester", role=role, world_id="shattered_realms", room_id="builder_test_room", level=1, hp=1, max_hp=1, mana=1, max_mana=1, stamina=1, max_stamina=1, xp=0, gold=0, inventory=[], equipment={}, abilities=[], affects={}, preferences={})


def test_player_denied_builder_command():
    e = MudCommandEngine()
    r = e.handle_command(char("player"), "builder on")
    assert not r.ok
    assert "permission" in r.narrative


def test_builder_crud_validate_snapshot_history_events():
    bus = EventBus(); seen=[]
    for name in ["builder_mode_enabled","builder_room_created","builder_room_updated","builder_exit_created","builder_feature_updated","builder_item_template_created","builder_entity_template_created","builder_spawn_created","builder_validation_run","builder_save_requested","builder_snapshot_created"]:
        bus.subscribe(name, lambda ev: seen.append(ev.event_name), source=name)
    e = MudCommandEngine(event_bus=bus); c = char("builder")
    assert e.handle_command(c, "builder on").ok
    assert e.handle_command(c, "rcreate builder_test_room").ok
    assert e.handle_command(c, "rname Builder Test Room").ok
    assert e.handle_command(c, "rdesc A safe draft room.").ok
    assert e.handle_command(c, "excreate north builder_test_room").ok
    assert e.handle_command(c, "fcreate fountain").ok
    assert "fountain" in e.handle_command(c, "look fountain").narrative.lower()
    assert e.handle_command(c, "ocreate widget").ok
    assert e.handle_command(c, "mcreate guide").ok
    assert e.handle_command(c, "spawncreate guide_spawn guide").ok
    assert e.handle_command(c, "builder validate").ok
    assert e.handle_command(c, "builder save").ok
    assert e.handle_command(c, "builder snapshot").ok
    assert "Recent builder history" in e.handle_command(c, "builder history").narrative
    assert "room_id" in e.handle_command(c, "rstat").narrative or "id" in e.handle_command(c, "rstat").narrative
    assert set(["builder_mode_enabled","builder_room_created","builder_room_updated","builder_exit_created","builder_item_template_created","builder_entity_template_created","builder_spawn_created","builder_validation_run","builder_save_requested","builder_snapshot_created"]).issubset(set(seen))


def test_builder_validate_catches_broken_exit():
    e = MudCommandEngine(); c = char("builder"); c.room_id="builder_broken_room"
    e.handle_command(c, "rcreate builder_broken_room")
    e.handle_command(c, "rname Broken")
    e.handle_command(c, "excreate west missing_room_for_validation")
    r = e.handle_command(c, "builder validate")
    assert not r.ok
    assert "missing room" in r.narrative
