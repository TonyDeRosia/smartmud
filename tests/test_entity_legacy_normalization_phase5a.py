from pathlib import Path

from engine.mud_runtime import MudRuntime


def test_legacy_room_npc_declaration_normalizes_to_deterministic_spawn(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    sid = rt._legacy_spawn_id("training_yard", "training_master_borik")
    spawns = rt._live_entity_spawns()
    assert sid == "legacy_training_yard_training_master_borik"
    assert sid in spawns
    assert spawns[sid]["plugin_data"]["legacy_source"]["normalized"] is True
    assert rt._materialization_row("entity_spawn", sid)
    assert [e["name"] for e in rt.get_room_contents("training_yard")["entity_instances"]] == ["Training Master Borik"]


def test_canonical_spawn_supersedes_equivalent_legacy_source(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    rt.active_world.spawns.append({"id": "canonical_borik", "entity_template_id": "training_master_borik", "room_id": "training_yard", "quantity": 1, "spawn_policy": "once"})
    spawns = rt._live_entity_spawns()
    assert "canonical_borik" in spawns
    assert rt._legacy_spawn_id("training_yard", "training_master_borik") not in spawns
