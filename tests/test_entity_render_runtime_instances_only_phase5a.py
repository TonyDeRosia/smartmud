from pathlib import Path

from engine.mud_runtime import MudRuntime


def test_quantity_two_same_name_runtime_instances_both_render(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    spawn = {"id": "test_two_harl", "entity_template_id": "blacksmith_harl", "room_id": "market_lane", "quantity": 2, "spawn_policy": "once"}
    rt.active_world.spawns.append(spawn)
    rt.materialize_entity_spawn("test_two_harl")
    names = [e["name"] for e in rt.get_room_contents("market_lane")["entity_instances"]]
    assert names.count("Blacksmith Harl") == 2
    ids = [e["instance_id"] for e in rt.get_room_contents("market_lane")["entity_instances"] if e["name"] == "Blacksmith Harl"]
    assert len(ids) == len(set(ids)) == 2


def test_room_contents_do_not_include_templates_spawns_legacy_or_materializations(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    contents = rt.get_room_contents("training_yard", include_builder_metadata=True)
    assert contents["entity_instances"]
    assert all(e.get("instance_id") and e.get("entity_id") for e in contents["entity_instances"])
    assert "entity_spawn_declarations" in contents
    assert "legacy_npc_declarations" in contents
    gameplay = rt.get_room_contents("training_yard")
    assert set(gameplay) == {"features", "item_instances", "entity_instances", "players", "exits"}
