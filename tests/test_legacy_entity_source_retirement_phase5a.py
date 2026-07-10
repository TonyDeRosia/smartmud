from pathlib import Path

from engine.mud_runtime import MudRuntime


def test_rcontents_reports_legacy_separately_and_rendering_source(tmp_path):
    rt = MudRuntime(Path.cwd(), tmp_path)
    rt.load_world("shattered_realms")
    cid = rt.create_character(world_id="shattered_realms", name="Builder")["character_id"]
    import sqlite3
    with sqlite3.connect(rt.state_store.db_path) as conn:
        conn.execute("UPDATE characters SET role='builder', builder_enabled=1, immortal_level=50 WHERE id=?", (cid,))
    rt.enter_world(cid)
    char = rt.state_store.load_character(cid)
    assert rt.goto_room(char, "training_yard")[0]
    out = rt.handle_input(cid, "rcontents here")["output"]
    assert "Runtime entity instances:" in out
    assert "Legacy room NPC declarations:" in out
    assert "Rendering source:\n- runtime entity instances only" in out
    assert "Training Master Borik" in out
    assert rt.handle_input(cid, "look")["output"].count("Training Master Borik") == 1
