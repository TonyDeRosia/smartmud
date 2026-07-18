"""Phase 21B.6 production acceptance: replay identity and transport parity.

These tests deliberately compose ``MudRuntime`` and use its real web/telnet
adapters.  ``TransportMessage`` carries retry identity as adapter metadata, not
as a player command extension.
"""
from pathlib import Path

from engine.mud_runtime import MudRuntime
from smart_mud.transport import TelnetTransportAdapter, TransportMessage, WebTransportAdapter


def _runtime(tmp_path, hp=1):
    runtime = MudRuntime(Path.cwd(), tmp_path)
    runtime.load_world("shattered_realms")
    character_id = runtime.create_character(world_id="shattered_realms", name="Phase Mage", class_id="mage")["character_id"]
    runtime.enter_world(character_id, session_id="phase21b6")
    character = runtime.active_characters[character_id]
    target = next(e for e in runtime.find_entities() if e.get("entity_type") in {"npc", "mob"})
    runtime.move_entity(target["entity_id"], character.room_id)
    runtime.update_entity_state(target["entity_id"], {"current_health": hp, "maximum_health": hp, "is_alive": True, "current_state": "standing"})
    runtime.actor_registry.get(runtime.actor_id_for_entity_instance(target)).resources.health = hp
    return runtime, character_id, target


def _cast(adapter, session, target_name, identity):
    return adapter.handle_message(TransportMessage(session, f"cast magic missile {target_name}", request_id=identity, idempotency_key=identity))


def test_browser_terminal_replay_preserves_original_terminal_receipt(tmp_path):
    runtime, character_id, target = _runtime(tmp_path)
    adapter = WebTransportAdapter(runtime); session = adapter.create_session(character_id=character_id, world_id="shattered_realms")
    first = _cast(adapter, session, target["name"], "browser-terminal-retry")
    original = first.metadata["result"]["ability_result"]
    mana = runtime.active_characters[character_id].mana
    duplicate = _cast(adapter, session, target["name"], "browser-terminal-retry")
    receipt = duplicate.metadata["result"]["ability_result"]
    assert original.ok and original.death_results and receipt.status == "DUPLICATE_IGNORED"
    assert receipt.damage_results == original.damage_results and receipt.death_results == original.death_results
    assert receipt.metadata["original_request_id"] == original.request_id
    assert runtime.active_characters[character_id].mana == mana
    assert runtime.find_entity(target["entity_id"]) is None


def test_telnet_terminal_replay_preserves_receipt_and_plain_output(tmp_path):
    runtime, character_id, target = _runtime(tmp_path)
    adapter = TelnetTransportAdapter(runtime); session = adapter.create_session(character_id=character_id, world_id="shattered_realms")
    first = _cast(adapter, session, target["name"], "telnet-terminal-retry")
    original = first.metadata["result"]["ability_result"]
    duplicate = _cast(adapter, session, target["name"], "telnet-terminal-retry")
    receipt = duplicate.metadata["result"]["ability_result"]
    assert receipt.status == "DUPLICATE_IGNORED"
    assert receipt.death_results == original.death_results
    assert "<" not in duplicate.output and "<" not in duplicate.prompt


def test_browser_and_telnet_nonterminal_magic_missile_have_equivalent_receipts(tmp_path):
    outcomes = []
    for adapter_type in (WebTransportAdapter, TelnetTransportAdapter):
        runtime, character_id, target = _runtime(tmp_path / adapter_type.__name__, hp=100)
        adapter = adapter_type(runtime); session = adapter.create_session(character_id=character_id, world_id="shattered_realms")
        response = _cast(adapter, session, target["name"], adapter_type.__name__)
        result = response.metadata["result"]["ability_result"]
        assert result.ok and result.damage_results and not result.death_results
        damage = result.damage_results[0]
        assert not damage["terminal"] and runtime.find_entity(target["entity_id"]) is not None
        outcomes.append((result.ability_id, result.paid_costs, damage["final_amount"], damage["terminal"]))
    assert outcomes[0] == outcomes[1]


def test_terminal_receipt_idempotency_survives_mudruntime_recreation(tmp_path):
    runtime, character_id, target = _runtime(tmp_path)
    adapter = WebTransportAdapter(runtime); session = adapter.create_session(character_id=character_id, world_id="shattered_realms")
    first = _cast(adapter, session, target["name"], "restart-terminal-retry")
    original = first.metadata["result"]["ability_result"]
    mana = runtime.active_characters[character_id].mana
    # A new production composition reloads the same durable database.
    restarted = MudRuntime(Path.cwd(), tmp_path); restarted.load_world("shattered_realms")
    restarted.enter_world(character_id, session_id="phase21b6-restarted")
    replay = WebTransportAdapter(restarted)
    response = _cast(replay, replay.create_session(character_id=character_id, world_id="shattered_realms"), target["name"], "restart-terminal-retry")
    duplicate = response.metadata["result"]["ability_result"]
    assert duplicate.status == "DUPLICATE_IGNORED"
    assert duplicate.damage_results == original.damage_results
    assert duplicate.death_results == original.death_results
    assert restarted.active_characters[character_id].mana == mana
    assert restarted.find_entity(target["entity_id"]) is None
