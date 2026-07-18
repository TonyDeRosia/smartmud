import sqlite3


def _make_builder(isolated_builder_world):
    rt = isolated_builder_world.runtime
    acct = rt.create_account("Phase Hotfix Builder", role="owner")
    rt.load_world("shattered_realms")
    cid = rt.create_character(world_id="shattered_realms", name="Phase Hotfix Builder", account_id=acct["account_id"])["character_id"]
    rt.enter_world(cid, session_id="phase15b32-hotfix")
    rt.handle_input(cid, "builder on")
    return rt, cid


def _out(rt, cid, command):
    return rt.handle_input(cid, command)["output"]


def _history(rt, cid):
    with sqlite3.connect(rt.state_store.db_path) as con:
        return [r[0] for r in con.execute("SELECT command FROM command_history WHERE character_id=? ORDER BY id", (cid,))]


def test_root_q_routes_through_production_input_path_and_closes_clean_editor(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    opened = _out(rt, cid, "medit 1501")
    assert "Mob ID" in opened
    char = rt.active_characters[cid]
    assert rt.command_engine.builder_service.sessions.has(char)

    closed = _out(rt, cid, "q")

    assert "Which command did you mean?" not in closed
    assert "Goodbye" not in closed
    assert "Editor closed and lock released" in closed
    assert cid in rt.active_characters
    assert not rt.command_engine.builder_service.sessions.has(char)
    assert "q" not in _history(rt, cid)
    assert "Guildhall" in _out(rt, cid, "look")


def test_uppercase_q_and_full_quit_are_local_while_editor_active(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    assert "Mob ID" in _out(rt, cid, "medit 1501")
    closed = _out(rt, cid, "Q")
    assert "Which command did you mean?" not in closed
    assert "Editor closed and lock released" in closed
    assert cid in rt.active_characters

    assert "Mob ID" in _out(rt, cid, "medit 1501")
    closed = _out(rt, cid, "quit")
    assert "Which command did you mean?" not in closed
    assert "Editor closed and lock released" in closed
    assert cid in rt.active_characters
    hist = _history(rt, cid)
    assert "Q" not in hist
    assert "quit" not in hist


def test_submenu_q_returns_to_root_and_unknown_alpha_is_local(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    assert "Mob ID" in _out(rt, cid, "medit 1501")
    submenu = _out(rt, cid, "9")
    assert "MOB BUILD" in submenu
    root = _out(rt, cid, "q")
    assert "Which command did you mean?" not in root
    assert "Mob ID" in root
    assert "Commands: level <n>" not in root

    unknown = _out(rt, cid, "quest")
    assert "Which command did you mean?" not in unknown
    assert "Invalid editor input" in unknown
    assert rt.command_engine.builder_service.sessions.has(rt.active_characters[cid])
    hist = _history(rt, cid)
    assert "5" not in hist
    assert "q" not in hist
    assert "quest" not in hist


def test_global_q_unchanged_without_active_editor(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    output = _out(rt, cid, "q")
    assert "Which command did you mean? quaff, quest, questlog, quests, quit" in output
    assert "q" in _history(rt, cid)


def test_phase16g_medit_u_routes_to_combat_abilities_not_up(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    assert "Mob ID" in _out(rt, cid, "medit apprentice_mage_lina")
    lower = _out(rt, cid, "u")
    assert "Combat Abilities" in lower
    assert "A) Add   E) Edit   D) Delete   T) Toggle   Q) Quit" in lower
    assert "You cannot go that way." not in lower
    root = _out(rt, cid, "q")
    assert "Mob ID" in root
    upper = _out(rt, cid, "U")
    assert "Combat Abilities" in upper
    assert "You cannot go that way." not in upper
    assert "u" not in _history(rt, cid)


def test_phase16g_medit_visible_alias_collisions_stay_in_builder(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    assert "Mob ID" in _out(rt, cid, "medit apprentice_mage_lina")
    for key, expected in [("I", "Mob Identity"), ("R", "Loadout / Loot"), ("S", "Scripts"), ("V", "Event Reactions")]:
        out = _out(rt, cid, key)
        assert expected in out
        assert "You cannot go that way." not in out
        assert "You are already resting" not in out
        assert "Inventory" not in out or key == "R"
        if key in {"R", "S", "V"}:
            assert "Mob ID" in _out(rt, cid, "q")
        elif key == "I":
            assert "Mob ID" in _out(rt, cid, "q")


def test_phase16g_advanced_slot_fields_mutate_draft(isolated_builder_world):
    rt, cid = _make_builder(isolated_builder_world)
    assert "Mob ID" in _out(rt, cid, "medit apprentice_mage_lina")
    assert "Combat Abilities" in _out(rt, cid, "u")
    assert "Combat Ability Editor" in _out(rt, cid, "a")
    assert "Enter value for ability id" in _out(rt, cid, "2")
    assert "fireball" in _out(rt, cid, "fireball")
    assert "Enter value for trigger" in _out(rt, cid, "4")
    assert "cooldown_ready" in _out(rt, cid, "cooldown")
    assert "Enter value for timing" in _out(rt, cid, "5")
    assert "cooldown=3" not in _out(rt, cid, "cooldown=3 minimum_round=1 chance=100")
    ability_list = _out(rt, cid, "q")
    assert "Combat Abilities" in ability_list and "fireball" in ability_list
    assert "Mob ID" in _out(rt, cid, "q")
    assert "Event Reactions" in _out(rt, cid, "v")
    assert "Event Reaction Editor" in _out(rt, cid, "a")
    assert "Enter value for event type" in _out(rt, cid, "1")
    assert "Event Reaction Editor" in _out(rt, cid, "player_enters")
    assert "Enter value for action data" in _out(rt, cid, "3")
    assert "Field updated." in _out(rt, cid, "hello there")
    sess = rt.command_engine.builder_service.sessions.active[rt.command_engine.builder_service.sessions.actor_key(rt.active_characters[cid])]
    assert (sess.working_record["event_reactions"][0]["action_data"] or {}).get("text") == "hello there"
