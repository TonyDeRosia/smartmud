import sqlite3
from engine.crafting import CraftingService, CraftingContent, init_crafting_schema


def make_service(tmp_path):
    db=tmp_path/'craft.db'
    init_crafting_schema(db)
    with sqlite3.connect(db) as con:
        con.execute("CREATE TABLE IF NOT EXISTS item_instances(instance_id TEXT PRIMARY KEY,world_id TEXT,template_id TEXT,owner_type TEXT,owner_id TEXT,room_id TEXT,equipped_slot TEXT,stack_count INTEGER DEFAULT 1,condition TEXT DEFAULT 'normal',durability INTEGER DEFAULT 100,created_at TEXT,updated_at TEXT,custom_flags JSON,plugin_data JSON,destroyed_at TEXT,destroy_reason TEXT)")
        for iid,tid in [('ore1','iron_ore'),('ore2','iron_ore'),('herb1','starter_herb'),('sword1','training_sword')]:
            con.execute("INSERT OR IGNORE INTO item_instances(instance_id,world_id,template_id,owner_type,owner_id,room_id,equipped_slot,stack_count,condition,durability,created_at,updated_at,custom_flags,plugin_data) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(iid,'shattered_realms',tid,'actor','actor1','','',1,'normal',100,'1','1','{}','{}'))
    svc=CraftingService(db, runtime=None)
    svc.grant_profession('actor1','blacksmith')
    svc.grant_profession('actor1','herbalist')
    svc.grant_profession('actor1','salvager')
    return svc


def test_phase7c_content_validates_and_loads():
    content=CraftingContent('worlds/shattered_realms')
    assert content.get('recipe_definitions','iron_sword_recipe')
    assert content.get('workstation_profiles','guild_blacksmith_anvil')
    assert content.validate()['errors'] == []


def test_phase7c_preview_reservation_cancel_and_complete(tmp_path):
    svc=make_service(tmp_path)
    preview=svc.preview_recipe('actor1','training_sword_recipe',1)
    assert preview.eligible
    assert preview.details['selected_inputs'][0]['item_instance_id'] == 'ore1'
    job=svc.start_crafting('actor1','training_sword_recipe',1,world_time=1)
    assert job['status'] == 'completed'
    assert svc.get_crafting_job(job['crafting_job_id'])['result_reward_packet_id']
    again=svc.complete_crafting_job(job['crafting_job_id'],1)
    assert again['status'] == 'completed'


def test_phase7c_timed_cancellation_releases(tmp_path):
    svc=make_service(tmp_path)
    job=svc.start_crafting('actor1','iron_sword_recipe',1,world_time=5)
    assert job['status'] == 'in_progress'
    cancelled=svc.cancel_crafting('actor1',job['crafting_job_id'])
    assert cancelled['status'] == 'cancelled'


def test_phase7c_profession_and_knowledge(tmp_path):
    svc=make_service(tmp_path)
    svc.grant_recipe('actor1','iron_sword_recipe','admin')
    assert svc.actor_knows_recipe('actor1','iron_sword_recipe')
    st=svc.award_profession_experience('actor1','blacksmith',125)
    assert st['total_experience'] >= 125


def test_phase7c_salvage_preview_warns(tmp_path):
    svc=make_service(tmp_path)
    svc.grant_profession('actor1','salvager')
    p=svc.preview_recipe('actor1','scrap_salvage_recipe',1)
    assert any('destructive' in w for w in p.details['warnings'])
