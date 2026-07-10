from pathlib import Path
import sqlite3

from engine.mud_runtime import MudRuntime

ROOM_EXPECTATIONS = {
    "blacksmith_stall": "Blacksmith Harl",
    "training_yard": "Training Master Borik",
    "spell_practice_circle": "Apprentice Mage Lina",
    "healer_corner": "Healer Sella",
}


def make_runtime(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    cid = rt.create_character(world_id="shattered_realms", name="Integrity Tester")["character_id"]
    import sqlite3
    with sqlite3.connect(rt.state_store.db_path) as conn:
        conn.execute("UPDATE characters SET role='builder', builder_enabled=1, immortal_level=50 WHERE id=?", (cid,))
    rt.enter_world(cid)
    char = rt.state_store.load_character(cid)
    return rt, cid, char


def test_real_shattered_realms_rooms_render_one_runtime_npc_only(tmp_path):
    rt, cid, char = make_runtime(tmp_path)
    for room_id, name in ROOM_EXPECTATIONS.items():
        ok, msg = rt.goto_room(char, room_id)
        assert ok, msg
        contents = rt.get_room_contents(room_id, include_builder_metadata=True)
        assert [e["name"] for e in contents["entity_instances"]].count(name) == 1
        assert contents["legacy_npc_declarations"]
        assert all("source" in d for d in contents["legacy_npc_declarations"])
        look = rt.handle_input(cid, "look")["output"]
        assert look.count(name) == 1
        assert "Entity runtime source integrity: PASS" in rt.handle_input(cid, "entityaudit here")["output"]


def test_real_shattered_realms_materialization_is_stable_across_reload(tmp_path):
    rt, _cid, _char = make_runtime(tmp_path)
    before = {rid: [e["instance_id"] for e in rt.get_room_contents(rid)["entity_instances"]] for rid in ROOM_EXPECTATIONS}
    rt.materialize_world_content("shattered_realms")
    for rid in ROOM_EXPECTATIONS:
        rt.materialize_room_content("shattered_realms", rid)
    after = {rid: [e["instance_id"] for e in rt.get_room_contents(rid)["entity_instances"]] for rid in ROOM_EXPECTATIONS}
    assert after == before
    rt2 = MudRuntime(Path.cwd(), tmp_path)
    rt2.load_world("shattered_realms")
    restarted = {rid: [e["instance_id"] for e in rt2.get_room_contents(rid)["entity_instances"]] for rid in ROOM_EXPECTATIONS}
    assert restarted == before


def test_upgraded_database_existing_legacy_row_is_adopted(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    with sqlite3.connect(rt.state_store.db_path) as conn:
        conn.execute("DELETE FROM content_materializations WHERE declaration_kind='entity_spawn' AND declaration_id='legacy_training_yard_training_master_borik'")
        rows = conn.execute("SELECT entity_id FROM entity_instances WHERE template_id='training_master_borik'").fetchall()
        assert len(rows) == 1
    rt.materialize_entity_spawn("legacy_training_yard_training_master_borik")
    contents = rt.get_room_contents("training_yard")
    assert [e["name"] for e in contents["entity_instances"]] == ["Training Master Borik"]
    row = rt._materialization_row("entity_spawn", "legacy_training_yard_training_master_borik")
    assert row and len(row["instance_ids"]) == 1
