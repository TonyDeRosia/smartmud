from pathlib import Path
import sqlite3

from engine.survival_needs import SurvivalNeedsService


def test_rest_sleep_sessions_are_persistent_and_idempotent(tmp_path):
    db=tmp_path/'s.db'; svc=SurvivalNeedsService(db, Path('worlds/shattered_realms'), 'shattered_realms')
    svc.initialize_actor_needs('char_rest')
    svc.set_actor_need('char_rest','fatigue',40,'test')
    r=svc.start_rest('char_rest')
    assert r['ok'] and r['status']=='resting'
    assert not svc.start_sleep('char_rest')['ok']
    svc.process_rest_sessions('shattered_realms', r['planned_end_world_time'])
    done=svc.complete_rest(r['rest_session_id'])
    dup=svc.complete_rest(r['rest_session_id'])
    assert done['ok'] and dup['duplicate']
    assert svc.get_actor_need('char_rest','fatigue')['current_value'] > 40
    svc2=SurvivalNeedsService(db, Path('worlds/shattered_realms'), 'shattered_realms')
    assert svc2.trace_rest(r['rest_session_id'])['status']=='completed'


def test_sleep_wake_and_shelter_context(tmp_path):
    db=tmp_path/'s.db'; svc=SurvivalNeedsService(db, Path('worlds/shattered_realms'), 'shattered_realms')
    s=svc.start_sleep('char_sleep','basic_bed')
    assert s['ok'] and s['quality_score'] >= 45
    ctx=svc.get_rest_context('char_sleep')
    assert ctx['active_session']['rest_type']=='sleep'
    w=svc.wake_actor('char_sleep','test_wake')
    assert w['status']=='interrupted'
    assert svc.get_rest_context('char_sleep')['active_session'] is None


def test_campfire_and_campsite_runtime_state(tmp_path):
    db=tmp_path/'s.db'; svc=SurvivalNeedsService(db, Path('worlds/shattered_realms'), 'shattered_realms')
    cf=svc.create_campfire('char_camp','basic_campfire','room_a')
    assert svc.light_campfire('char_camp', cf['campfire_instance_id'])['status']=='lit'
    assert svc.add_campfire_fuel('char_camp', cf['campfire_instance_id'], 'item_firewood')['fuel_added']==1
    assert svc.add_campfire_fuel('char_camp', cf['campfire_instance_id'], 'item_firewood')['duplicate']
    assert svc.extinguish_campfire('char_camp', cf['campfire_instance_id'])['status']=='extinguished'
    cs=svc.create_campsite('char_camp','basic_campsite','room_a')
    assert svc.trace_campsite(cs['campsite_instance_id'])['room_id']=='room_a'
    assert svc.dismantle_campsite('char_camp', cs['campsite_instance_id'])['status']=='dismantled'
    with sqlite3.connect(db) as c:
        assert c.execute('select fuel_current from campfire_instances').fetchone()[0] == 1
