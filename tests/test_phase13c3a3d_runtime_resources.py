from engine.actors import Actor
from engine.runtime_resources import RuntimeResourceService, ResourceMutationResult, LifecycleTransitionResult
from engine.mud_state_store import MUDStateStore


def test_runtime_resource_service_persists_character_resources(tmp_path):
    store = MUDStateStore('camp', world_id='world', db_path=tmp_path/'mud.sqlite')
    store.initialize()
    store.save_character(character_id='c1', world_id='world', name='Hero', hp_current=50, mana_current=20, stamina_current=30)
    actor = Actor.create('character:c1', 'Hero')
    actor.resources.health = 50
    actor.resources.maximum_health = 100
    svc = RuntimeResourceService(db_path=store.db_path, world_id='world')

    result = svc.apply_damage(actor, 12, action_id='hit-1')

    assert isinstance(result, ResourceMutationResult)
    assert result.ok
    assert result.before == 50
    assert result.after == 38
    assert actor.resources.health == 38
    assert store.load_character('c1')['hp_current'] == 38
    assert store.load_character_stats('c1')['health'] == 38


def test_runtime_resource_service_clamps_and_lifecycle_once(tmp_path):
    store = MUDStateStore('camp', world_id='world', db_path=tmp_path/'mud.sqlite')
    store.initialize()
    actor = Actor.create('entity:rat1', 'Rat')
    actor.resources.health = 5
    actor.resources.maximum_health = 5
    svc = RuntimeResourceService(db_path=store.db_path, world_id='world')

    dmg = svc.apply_damage(actor, 99, action_id='kill-1')
    first = svc.evaluate_zero_health(actor, trigger_action_id='kill-1')
    second = svc.evaluate_zero_health(actor, trigger_action_id='kill-1')

    assert dmg.after == 0
    assert isinstance(first, LifecycleTransitionResult)
    assert first.ok and first.new_state == 'dead' and not first.already_processed
    assert second.ok and second.already_processed
