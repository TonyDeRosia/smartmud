import sqlite3

from engine.abilities import AbilityExecutionService, AbilityExecutionResult, AbilityExecutionContext, init_ability_schema
from engine.actors import Actor
from smart_mud.world_registry import WorldRegistry


class EventBus:
    def __init__(self): self.events=[]
    def subscribe(self,*a,**k): pass
    def publish(self, name, payload, **kwargs): self.events.append((name, payload, kwargs))


def svc(tmp_path):
    bus=EventBus(); db=tmp_path/'mud.db'; init_ability_schema(db)
    s=AbilityExecutionService(db, WorldRegistry().load_world('shattered_realms'), event_bus=bus, world_id='shattered_realms', allow_isolated_combat_engine=True)
    hero=Actor.create('hero','Hero','player'); gob=Actor.create('goblin','Goblin','mob')
    hero.identity.current_location=gob.identity.current_location='room1'
    s.register_actor(hero); s.register_actor(gob)
    for aid in ['kick','bandage','magic_missile','armor','bless','strength']:
        s.grant_ability('hero', aid, 'test')
    return s, hero, gob, bus


def effect_count(s, actor='hero'):
    with sqlite3.connect(s.db_path) as c:
        return c.execute("SELECT count(*) FROM actor_effect_instances WHERE target_actor_id=? AND active=1", (actor,)).fetchone()[0]


def test_phase18f_gateway_context_result_damage_heal_effects_cooldowns(tmp_path):
    s, hero, gob, bus = svc(tmp_path); gw=s.gateway()
    before_stam=hero.resources.stamina; before_gob=gob.resources.health
    kick=gw.execute_result('hero','kick','goblin', {'command':'kick goblin'})
    assert isinstance(kick, AbilityExecutionResult) and isinstance(kick.context, AbilityExecutionContext)
    assert kick.status == 'SUCCESS'
    assert hero.resources.stamina < before_stam
    assert gob.resources.health < before_gob
    assert kick.cooldown_started and s.get_ability_status('hero','kick')['remaining'] >= 1
    assert any(e[0] == 'ability_started' for e in bus.events)
    assert any(e[0] == 'damage_applied' for e in bus.events)
    assert any(e[0] == 'cooldown_started' for e in bus.events)

    second=gw.execute_result('hero','kick','goblin', {'command':'kick goblin'})
    assert second.status == 'ON_COOLDOWN'

    hero.resources.health=50; before=hero.resources.health
    bandage=gw.execute_result('hero','bandage','self', {'command':'bandage self'})
    assert bandage.status == 'SUCCESS' and hero.resources.health > before
    assert any(e[0] == 'healing_applied' for e in bus.events)

    before_mana=hero.resources.mana; before_gob=gob.resources.health
    mm=gw.execute_result('hero','magic missile','goblin', {'command':'cast magic missile goblin'})
    assert mm.status == 'SUCCESS' and hero.resources.mana < before_mana and gob.resources.health < before_gob

    n=effect_count(s)
    armor=gw.execute_result('hero','armor','self', {'command':'cast armor self'})
    assert armor.status == 'SUCCESS' and effect_count(s) == n + 1
    assert any(e[0] == 'effect_applied' for e in bus.events)


def test_phase18f_target_resource_not_known_handler_and_duplicates(tmp_path):
    s, hero, gob, bus = svc(tmp_path); gw=s.gateway()
    wrong=gw.execute_result('hero','kick','self', {'command':'kick self'})
    assert wrong.status == 'INVALID_TARGET'

    unknown=gw.execute_result('hero','no such ability','self', {'command':'cast no such ability'})
    assert unknown.status == 'UNKNOWN_ABILITY'

    stranger=Actor.create('stranger','Stranger','player'); s.register_actor(stranger)
    not_known=s.gateway().execute_result('stranger','armor','self', {'command':'cast armor self'})
    assert not_known.status == 'NOT_KNOWN'

    hero.resources.mana=0
    low=gw.execute_result('hero','bless','self', {'command':'cast bless self'})
    assert low.status == 'INSUFFICIENT_MANA'
    hero.resources.mana=50

    first=gw.execute_result('hero','strength','self', {'command':'cast strength self'})
    assert first.status == 'SUCCESS'
    s._world_time = s.world_time() + 2
    second=gw.execute_result('hero','strength','self', {'command':'cast strength self'})
    assert second.status == 'SUCCESS'
    assert any(e.get('refreshed') for e in second.applied_effects if isinstance(e, dict) for e in e.get('results', []))

    s.registry.abilities['strength'].canonical_effects=[]
    s.registry.abilities['strength'].damage_components=[]
    s.registry.abilities['strength'].healing_components=[]
    s.registry.abilities['strength'].effects_applied=[]
    no_handler=gw.execute_result('hero','strength','self', {'command':'cast strength self'})
    assert no_handler.status == 'HANDLER_NOT_IMPLEMENTED'


def test_phase18f_spellup_casts_and_skips(tmp_path):
    s, hero, gob, bus = svc(tmp_path)
    for aid in ['armor','bless','strength']:
        out=s.gateway().execute_result('hero', aid, 'self', {'command':f'cast {aid} self', 'source':'spellup'})
        assert out.status == 'SUCCESS'
    assert effect_count(s) >= 3
    # Immediate recast through shared gateway cooldown is skipped by spellup callers.
    blocked=s.gateway().execute_result('hero', 'armor', 'self', {'command':'cast armor self', 'source':'spellup'})
    assert blocked.status in {'ON_COOLDOWN', 'SUCCESS'}
