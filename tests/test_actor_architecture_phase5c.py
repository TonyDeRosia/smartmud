from pathlib import Path

from engine.actors import Actor, ActorIdentity, FormulaRegistry, actor_from_runtime_character, default_derived_statistics
from engine.mud_runtime import MudCharacter, MudStateStore
from engine.score_renderer import ActorScoreRenderer


def test_actor_creation_has_every_core_profile_and_combat_capable_civilian():
    actor = Actor.create("npc_civilian", "Civilian", "npc")
    assert actor.combat_profile["aggression"] == "never"
    assert actor.combat_profile["attack"] == "none"
    for attr in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        assert attr in actor.attributes
    assert {"relationship_profile", "need_profile", "goal_profile", "memory_profile", "simulation_profile", "plugin_data"}.issubset(actor.to_dict())


def test_actor_serialization_and_sqlite_persistence(tmp_path: Path):
    actor = Actor.create("char_tester", "Tester", "player")
    actor.attributes["luck"] = 7
    char = MudCharacter(id="char_tester", name="Tester", role="player", actor_data=actor.to_dict())
    store = MudStateStore(tmp_path / "mud.db")
    store.save_character(char, "test_world")
    loaded = store.load_character("char_tester")
    assert loaded is not None
    restored = Actor.from_dict(loaded.actor_data)
    assert restored.identity.name == "Tester"
    assert restored.attributes["luck"] == 7


def test_modular_score_and_individual_sections_are_single_renderer_path():
    actor = Actor.create("char_score", "Jeromaru", "player")
    renderer = ActorScoreRenderer()
    full = renderer.render(actor)
    resources = renderer.render(actor, "resources")
    assert "Identity" in full and "Resources" in full and "Combat" in full
    assert resources.startswith("{system}============================================================================")
    assert "Health" in resources and "Mana" in resources
    assert renderer._renderers["resources"] == renderer.render_resources


def test_builder_diagnostics_admin_only_and_formula_placeholders():
    actor = Actor.create("char_diag", "Diag", "player")
    actor.attributes["builder_future_stat"] = None
    renderer = ActorScoreRenderer()
    assert "restricted" in renderer.render(actor, "builder_diagnostics", admin=False)
    diagnostics = renderer.render(actor, "builder_diagnostics", admin=True)
    assert "Future Formula Names" in diagnostics
    assert "Missing base attributes" in diagnostics
    assert "attack_rating" in diagnostics


def test_actor_inheritance_for_runtime_character_and_future_builder_attributes():
    char = MudCharacter(id="char_runtime", name="Runtime", role="player", hp=12, max_hp=34, gold=9)
    actor = actor_from_runtime_character(char, "shattered_realms")
    actor.attributes["honor"] = 15
    assert actor.actor_id == "char_runtime"
    assert actor.resources.health == 12
    assert actor.plugin_data["currencies"]["gold"] == 9
    assert actor.attributes["honor"] == 15


def test_formula_registry_placeholders_register_without_calculations():
    registry = FormulaRegistry.default()
    registry.register("builder_custom_rating")
    stats = default_derived_statistics({"builder_custom_rating": "builder_custom_rating"})
    assert registry.has("attack_rating")
    assert registry.has("builder_custom_rating")
    assert stats["attack_rating"].value is None
    assert stats["builder_custom_rating"].formula_name == "builder_custom_rating"
