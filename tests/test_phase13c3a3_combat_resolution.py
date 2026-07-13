from engine.actors import Actor, ActorResources
from engine.character_stats import CharacterAttributeService, CombatStatService, StatModifier
from engine.combat import CombatEngine, CombatResolutionContext, AttackKind


def make_actor(actor_id, attrs=None, hp=100):
    a=Actor.create(actor_id, actor_id.title())
    a.attributes.update(attrs or {})
    a.resources=ActorResources(health=hp, maximum_health=hp)
    return a


def service():
    attr=CharacterAttributeService(state_store=None)
    return CombatStatService(attr)


def test_canonical_hit_damage_armor_resistance_and_critical_are_snapshot_driven():
    stats=service()
    engine=CombatEngine(combat_stats=stats, seed='phase13c3a3')
    attacker=make_actor('attacker', {'strength':20, 'dexterity':20, 'constitution':10, 'intelligence':10, 'wisdom':10, 'charisma':10})
    defender=make_actor('defender', {'strength':10, 'dexterity':1, 'constitution':10, 'intelligence':10, 'wisdom':10, 'charisma':10})
    defender.resistance_profile={'physical': 25}
    result=engine.resolution.resolve(attacker, defender, CombatResolutionContext(attacker_id='attacker', defender_id='defender', action_id='sure_hit'))
    assert result.ok and result.hit
    assert result.raw_amount > result.final_amount
    assert result.resource_changes[0].after == 100 - result.final_amount
    assert result.diagnostics['trace'][1]['step'] == 'attack_roll_resolved'


def test_deterministic_miss_returns_structured_result_and_messages():
    stats=service()
    engine=CombatEngine(combat_stats=stats, seed='phase13c3a3')
    engine.resolution.rng=lambda *parts: 100
    attacker=make_actor('attacker', {'strength':1, 'dexterity':1, 'constitution':10, 'intelligence':10, 'wisdom':10, 'charisma':10})
    defender=make_actor('defender', {'strength':10, 'dexterity':30, 'constitution':10, 'intelligence':10, 'wisdom':10, 'charisma':10})
    result=engine.resolution.resolve(attacker, defender, CombatResolutionContext(attacker_id='attacker', defender_id='defender'))
    assert result.ok and not result.hit
    assert result.reason_code == 'miss'
    assert 'miss' in result.messages['attacker'].lower()


def test_healing_kind_clamps_to_maximum_and_uses_healing_result():
    stats=service()
    engine=CombatEngine(combat_stats=stats, seed='phase13c3a3')
    engine.resolution.rng=lambda *parts: 1
    healer=make_actor('healer', {'strength':10, 'dexterity':20, 'constitution':10, 'intelligence':10, 'wisdom':20, 'charisma':10})
    target=make_actor('target', {'strength':10, 'dexterity':1, 'constitution':10, 'intelligence':10, 'wisdom':10, 'charisma':10}, hp=100)
    target.resources.health=95
    result=engine.resolution.resolve(healer, target, CombatResolutionContext(attacker_id='healer', defender_id='target', attack_kind=AttackKind.HEALING.value))
    assert result.ok and result.hit
    assert target.resources.health == 100
    assert result.resource_changes[0].operation == 'healing'
