"""Production-boundary checks for spell provenance in combat narration."""
from pathlib import Path

from engine.mud_runtime import MudRuntime
from smart_mud.transport import TransportMessage, WebTransportAdapter


def _runtime_with_target(tmp_path, hp):
    runtime = MudRuntime(Path.cwd(), tmp_path)
    runtime.load_world("shattered_realms")
    character_id = runtime.create_character(world_id="shattered_realms", name="Spell Tester", class_id="mage")["character_id"]
    runtime.enter_world(character_id, session_id="spell-message-test")
    target = next(e for e in runtime.find_entities() if e.get("entity_type") in {"npc", "mob"})
    runtime.move_entity(target["entity_id"], runtime.active_characters[character_id].room_id)
    runtime.update_entity_state(target["entity_id"], {"current_health": hp, "maximum_health": hp, "is_alive": True, "current_state": "standing"})
    runtime.actor_registry.get(runtime.actor_id_for_entity_instance(target)).resources.health = hp
    return runtime, character_id, runtime.find_entity(target["entity_id"])


def test_terminal_magic_missile_uses_spell_provenance_not_physical_fallback(tmp_path):
    runtime, character_id, target = _runtime_with_target(tmp_path, 1)
    adapter = WebTransportAdapter(runtime)
    session = adapter.create_session(character_id=character_id, world_id="shattered_realms")

    response = adapter.handle_message(TransportMessage(session, f"cast magic missile {target['name']}"))
    receipt = response.metadata["result"]["ability_result"]
    queued = runtime.async_messages(character_id)
    text = (response.output + "\n" + "\n".join(row.get("message", "") for row in queued.get("messages", []))).lower()

    assert receipt.ok and receipt.damage_results[0]["terminal"]
    assert receipt.damage_results[0]["combat_result"]["messages"]
    assert "magic missile" in text
    assert "your magic missile defeats" in text
    assert "punch" not in text and "your attack defeats" not in text
    assert not runtime.combat_runtime.find_actor_encounter(f"character:{character_id}")


def test_nonterminal_spell_starts_engagement_without_opening_basic_attack(tmp_path):
    runtime, character_id, target = _runtime_with_target(tmp_path, 100)
    adapter = WebTransportAdapter(runtime)
    session = adapter.create_session(character_id=character_id, world_id="shattered_realms")

    response = adapter.handle_message(TransportMessage(session, f"cast magic missile {target['name']}"))
    receipt = response.metadata["result"]["ability_result"]
    damage = receipt.damage_results[0]
    history = list(runtime.combat_runtime.resident_encounters.values())

    assert receipt.ok and not damage["terminal"]
    assert damage["combat_result"]["messages"][0].startswith("Your Magic Missile strikes")
    assert runtime.combat_runtime.find_actor_encounter(f"character:{character_id}")
    assert len(history) == 1 and history[0].round_number == 0
    assert "punch" not in response.output.lower()
