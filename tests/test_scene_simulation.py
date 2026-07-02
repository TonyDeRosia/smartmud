from engine.scene_simulation import initialize_scene_v1_from_campaign, resolve_scene_action
from pathlib import Path
from engine.game_state_manager import GameStateManager


def _state(tmp_path):
    manager = GameStateManager(Path("data"), tmp_path / "saves")
    return manager.create_new_campaign(player_name="Mira", char_class="Mage", profile="classic_fantasy", mature_content_enabled=False, world_name="The Arcane Realm", world_theme="classic fantasy", starting_location_name="Old Gate", premise="A sealed warning says the north road has gone silent.")


def test_wizard_fantasy_scene_seeds_required_objects(tmp_path):
    scene = initialize_scene_v1_from_campaign(_state(tmp_path))
    kinds = {e["kind"] for e in scene["entities"]}
    assert "landmark" in kinds
    assert "npc" in kinds
    assert "object" in kinds
    assert len(scene["exits"]) >= 2
    assert scene["active_hooks"]


def test_look_around_returns_scene_contents(tmp_path):
    scene = initialize_scene_v1_from_campaign(_state(tmp_path))
    result = resolve_scene_action("i look around", scene)
    text = " ".join(result.messages)
    assert result.handled
    assert "Old Gate" in text
    assert "Local Messenger" in text
    assert "north road" in text.lower()
    assert "Hook:" in text


def test_read_notice_resolves_news(tmp_path):
    result = resolve_scene_action("read the news", initialize_scene_v1_from_campaign(_state(tmp_path)))
    assert result.handled
    assert "notice" in " ".join(result.messages).lower() or "urgent" in " ".join(result.messages).lower()


def test_talk_to_messenger_resolves_npc(tmp_path):
    result = resolve_scene_action("talk to messenger", initialize_scene_v1_from_campaign(_state(tmp_path)))
    assert result.handled
    assert "Local Messenger says" in " ".join(result.messages)


def test_go_north_updates_location(tmp_path):
    scene = initialize_scene_v1_from_campaign(_state(tmp_path))
    result = resolve_scene_action("go north", scene)
    assert result.handled
    assert result.state_updates["scene_v1"]["location_name"] == "North Road"


def test_unknown_object_lists_available(tmp_path):
    result = resolve_scene_action("inspect moon engine", initialize_scene_v1_from_campaign(_state(tmp_path)))
    assert result.handled
    assert "Available things" in " ".join(result.messages)

from app.web import WebRuntime
from models.base import NullNarrationAdapter


def test_wizard_campaign_scene_v1_handles_basic_ic_commands(tmp_path, monkeypatch):
    monkeypatch.setenv("ADVENTURERS_GUILD_USER_DATA", str(tmp_path / "user_data"))
    runtime = WebRuntime(Path.cwd())
    runtime.engine.model = NullNarrationAdapter()
    runtime.create_campaign({
        "slot": "slot_scene_v1",
        "character_name": "Mira",
        "character_role": "Mage",
        "rules_style": "Hybrid",
        "power_level": "Capable Adventurer",
        "starting_ability_mode": "suggest",
        "starting_item_mode": "suggest",
        "world_name": "The Arcane Realm",
        "world_theme": "classic fantasy",
        "starting_location_name": "Old Gate",
        "premise": "A sealed warning says the north road has gone silent.",
    })
    scene = runtime.session.state.structured_state.runtime.scene_state["scene_v1"]
    assert any(entity["kind"] == "npc" for entity in scene["entities"])
    look = runtime.handle_player_input("i look around")
    assert "Your character follows through" not in look["narrative"]
    assert "Local Messenger" in look["narrative"]
    read = runtime.handle_player_input("read the news")
    assert "notice" in read["narrative"].lower() or "urgent" in read["narrative"].lower()
    talk = runtime.handle_player_input("talk to messenger")
    assert "Local Messenger says" in talk["narrative"]
    move = runtime.handle_player_input("go north")
    assert runtime.session.state.structured_state.runtime.scene_state["scene_v1"]["location_name"] == "North Road"
