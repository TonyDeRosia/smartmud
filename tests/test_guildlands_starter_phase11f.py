import sqlite3
from pathlib import Path

from engine.gathering import GatheringService
from engine.quests import ConversationService, QuestContent, QuestEventRouter, QuestService, QuestValidator
from engine.rewards import RewardService, init_reward_schema

WORLD = Path('worlds/shattered_realms')

class Store:
    world_id = 'shattered_realms'
    def __init__(self, db): self.db_path = db
    def create_item_instance(self, iid, template_id, current_owner='', flags=None, creator=''):
        with sqlite3.connect(self.db_path) as con:
            con.execute('CREATE TABLE IF NOT EXISTS item_instances(unique_id TEXT PRIMARY KEY, template_id TEXT, current_owner TEXT, flags_json TEXT)')
            con.execute('INSERT OR IGNORE INTO item_instances VALUES(?,?,?,?)',(iid,template_id,current_owner,','.join(flags or [])))
        return {'instance_id': iid}

def services(tmp_path):
    db=tmp_path/'starter.db'; init_reward_schema(db); store=Store(db)
    rewards=RewardService(store=store, db_path=db, world_id='shattered_realms')
    qs=QuestService(db, WORLD, reward_service=rewards)
    gs=GatheringService(db, WORLD)
    return db, qs, gs

def test_starter_content_validates_and_references_existing_resource():
    content=QuestContent(WORLD)
    result=QuestValidator(content).validate_all()
    assert result.ok, result
    q=content.get('quest_definitions','guildlands_emberleaf_errand')
    assert q['offer_sources'][0]['source_id']=='guild_registrar_maren'
    obj=content.get('quest_objectives','guildlands_emberleaf_gather_one')
    assert obj['objective_type']=='harvest_resource'
    assert obj['target_definition']['item_template_id']=='emberleaf'
    assert content.get('conversation_definitions','maren_emberleaf_errand')

def test_fresh_actor_accepts_gathers_eventbus_progress_persists_and_turns_in_once(tmp_path):
    db, qs, gs = services(tmp_path); actor='fresh_recruit'
    assert qs.evaluate_quest_availability(actor,'guildlands_next_steps')['available'] is False
    conv=ConversationService(qs)
    start=conv.start_conversation(actor,'maren_emberleaf_errand','guild_registrar_maren')
    assert 'first field errand' in start['node']['text']
    offer=conv.choose(start['conversation_session_id'],1)
    assert 'Bring me one emberleaf' in offer['node']['text']
    accepted=conv.choose(start['conversation_session_id'],1)
    assert 'Gather the emberleaf' in accepted['node']['text']
    inst=qs.get_actor_quests(actor)[0]
    assert inst['quest_id']=='guildlands_emberleaf_errand'
    qs2=QuestService(db, WORLD)
    assert qs2.get_actor_quests(actor)[0]['status']=='active'
    node=gs.materialize_node('emberleaf_patch_crossing','guildhall_crossing_square')
    result=gs.gather_mode('harvest', actor, 'guildhall_crossing_square', 'emberleaf', 'training_sword', world_time=5)
    assert result['ok'] and result['item_template_id']=='emberleaf'
    routed=QuestEventRouter(qs).handle_event({'event_type':'resource_gathered','event_id':'gather-event-1', **result})
    assert routed['matched']==1
    assert QuestEventRouter(qs).handle_event({'event_type':'resource_gathered','event_id':'gather-event-1', **result})['matched']==0
    ready=qs.get_actor_quests(actor)[0]
    assert ready['status']=='ready_to_turn_in'
    journal=qs.get_quest_journal(actor)[0]
    assert journal['ready_to_turn_in'] is True
    assert journal['objectives'][0]['progress_current']==result['quantity']
    turned=qs.turn_in_quest(actor, ready['quest_instance_id'], {'source_type':'test'})
    assert turned['status']=='completed'
    packet_count=lambda: sqlite3.connect(db).execute('select count(*) from reward_packets').fetchone()[0]
    assert packet_count()==1
    qs.turn_in_quest(actor, ready['quest_instance_id'], {'source_type':'test'})
    assert packet_count()==1
    assert qs.evaluate_quest_availability(actor,'guildlands_next_steps')['available'] is True
    assert QuestService(db, WORLD).get_actor_quests(actor, 'completed')[0]['quest_id']=='guildlands_emberleaf_errand'

def test_insufficient_turnin_rejected_and_decline_branch(tmp_path):
    _, qs, _ = services(tmp_path); actor='decliner'
    conv=ConversationService(qs); start=conv.start_conversation(actor,'maren_emberleaf_errand','guild_registrar_maren')
    conv.choose(start['conversation_session_id'],1)
    decline=conv.choose(start['conversation_session_id'],2)
    assert decline['node']['id']=='maren_emberleaf_decline'
    inst=qs.accept_quest(actor,'guildlands_emberleaf_errand')
    try:
        qs.turn_in_quest(actor, inst['quest_instance_id'])
    except ValueError as exc:
        assert 'not ready' in str(exc)
    else:
        raise AssertionError('turn-in should reject insufficient progress')
