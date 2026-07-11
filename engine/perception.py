"""Canonical Phase 11B perception, stealth, trails, scent, sound, and search service.

One conservative service boundary owns sensory evidence state and detection
contests while querying EnvironmentService for light/weather/visibility context.
"""
from __future__ import annotations

import hashlib, json, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.environment import EnvironmentService
from engine.formulas import FormulaEngine

COLLECTIONS=("actor_sense_profiles","perception_profiles","concealment_profiles","concealment_source_profiles","search_profiles","tracking_profiles","terrain_trace_profiles","scent_profiles","sound_profiles","sound_propagation_profiles","perception_message_profiles","perception_knowledge_profiles","secret_discovery_profiles","sensory_retention_profiles")
CONCEALMENT_TYPES={"hidden","camouflaged","obscured","invisible_placeholder","disguised_placeholder","silent","scent_masked","concealed_item","hidden_feature","secret_exit","custom"}
STEALTH_STATUSES={"inactive","attempting","hidden","concealed","partially_revealed","revealed","broken","expired"}
DETECTION_RESULTS=("not_detected","hint","partial","silhouette","detected","identified")
TRAIL_TYPES={"footprint","scent","blood","drag","hoofprint","wheel_track","broken_vegetation","magical_placeholder","custom"}
SOUND_RESULTS=("inaudible","faint","muffled","audible","clear","identified_source")

def _read_records(root:Path, collection:str)->list[dict[str,Any]]:
    rows=[]
    for p in (root/collection/f"{collection}.json", root/"builder"/f"{collection}.json"):
        if not p.exists(): continue
        data=json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list): rows += [x for x in data if isinstance(x,dict)]
        elif isinstance(data, dict):
            value=data.get(collection) or data.get("records")
            rows += (value if isinstance(value,list) else [data])
    return rows

def _by_id(rows): return {str(r.get("id")):r for r in rows if r.get("id")}
def _json(v): return json.dumps(v or {}, sort_keys=True)
def _now(conn): return 0

def init_perception_schema(db_path:Path|str)->None:
    with sqlite3.connect(db_path) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS actor_stealth_state(stealth_state_id TEXT PRIMARY KEY,world_id TEXT,actor_id TEXT,concealment_profile_id TEXT,status TEXT,source_type TEXT,source_id TEXT,room_id TEXT,started_world_time INTEGER,last_updated_world_time INTEGER,movement_count INTEGER DEFAULT 0,concealment_score REAL DEFAULT 0,revealed_to_json TEXT DEFAULT '{}',expires_world_time INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,metadata_json TEXT DEFAULT '{}')""")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_actor_stealth_active ON actor_stealth_state(world_id,actor_id) WHERE status IN ('attempting','hidden','concealed','partially_revealed')")
        c.execute("""CREATE TABLE IF NOT EXISTS actor_perception_knowledge(knowledge_id TEXT PRIMARY KEY,world_id TEXT,observer_actor_id TEXT,target_type TEXT,target_id TEXT,knowledge_type TEXT,status TEXT,first_detected_world_time INTEGER,last_detected_world_time INTEGER,expires_world_time INTEGER,source_type TEXT,source_id TEXT,confidence REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,metadata_json TEXT DEFAULT '{}', UNIQUE(world_id,observer_actor_id,target_type,target_id,knowledge_type))""")
        c.execute("""CREATE TABLE IF NOT EXISTS item_concealment_state(concealment_state_id TEXT PRIMARY KEY,item_instance_id TEXT,room_id TEXT,container_id TEXT,concealed_by_actor_id TEXT,concealment_profile_id TEXT,concealment_score REAL,status TEXT,created_world_time INTEGER,revealed_world_time INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,metadata_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sensory_trails(trail_id TEXT PRIMARY KEY,world_id TEXT,trail_type TEXT,source_actor_id TEXT,source_type TEXT,source_id TEXT,room_id TEXT,from_room_id TEXT,to_room_id TEXT,direction TEXT,strength REAL,age_minutes INTEGER DEFAULT 0,created_world_time INTEGER,expires_world_time INTEGER,terrain_profile_id TEXT,weather_snapshot_json TEXT DEFAULT '{}',metadata_json TEXT DEFAULT '{}')""")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_sensory_trail_event ON sensory_trails(world_id,source_id,trail_type) WHERE source_id IS NOT NULL")
        c.execute("""CREATE TABLE IF NOT EXISTS actor_tracking_sessions(tracking_session_id TEXT PRIMARY KEY,actor_id TEXT,target_type TEXT,target_id TEXT,trail_type TEXT,status TEXT,current_room_id TEXT,last_trail_id TEXT,confidence REAL,started_world_time INTEGER,last_updated_world_time INTEGER,expires_world_time INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,metadata_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sensory_sound_events(sound_event_id TEXT PRIMARY KEY,world_id TEXT,source_type TEXT,source_id TEXT,source_actor_id TEXT,origin_room_id TEXT,sound_profile_id TEXT,intensity REAL,created_world_time INTEGER,expires_world_time INTEGER,event_id TEXT UNIQUE,metadata_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS perception_event_consumption(consumption_id TEXT PRIMARY KEY,world_id TEXT,consumer_type TEXT,consumer_id TEXT,event_id TEXT,event_type TEXT,operation TEXT,consumed_world_time INTEGER,metadata_json TEXT DEFAULT '{}', UNIQUE(world_id,consumer_type,consumer_id,event_id,operation))""")
        c.execute("""CREATE TABLE IF NOT EXISTS perception_audit_events(audit_event_id TEXT PRIMARY KEY,world_id TEXT,observer_actor_id TEXT,target_type TEXT,target_id TEXT,operation TEXT,result TEXT,score REAL,threshold REAL,source_event_id TEXT,room_id TEXT,world_time INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,metadata_json TEXT DEFAULT '{}')""")

@dataclass
class PerceptionService:
    db_path: Path|str
    world_root: Path|str
    world_id: str="shattered_realms"
    event_bus: Any=None
    environment: EnvironmentService|None=None
    formula_engine: FormulaEngine|None=None
    def __post_init__(self):
        self.db_path=Path(self.db_path); self.world_root=Path(self.world_root); init_perception_schema(self.db_path)
        self.records={c:_by_id(_read_records(self.world_root,c)) for c in COLLECTIONS}
        self.environment=self.environment or EnvironmentService(self.db_path,self.world_root,self.world_id,self.event_bus)
        self.formula_engine=self.formula_engine or FormulaEngine()
    def _id(self,*p): return "per_"+hashlib.sha256(":".join(map(str,p)).encode()).hexdigest()[:24]
    def _publish(self,name,payload):
        if self.event_bus and hasattr(self.event_bus,"publish"): self.event_bus.publish(name,payload)
    def validate_content(self):
        e=[]; w=[]
        visions=self.environment.records.get("actor_vision_profiles",{})
        for s in self.records["actor_sense_profiles"].values():
            for k in ("hearing_rating","scent_rating","awareness_rating","search_rating","tracking_rating","investigation_rating"):
                try:
                    if float(s.get(k,0))<0: e.append(f"Sense profile {s['id']} has negative {k}")
                except Exception: e.append(f"Sense profile {s.get('id')} invalid {k}")
            if s.get("vision_profile_id") and s["vision_profile_id"] not in visions: e.append(f"Sense profile {s['id']} references missing vision profile")
        for c in self.records["concealment_profiles"].values():
            if c.get("concealment_type") not in CONCEALMENT_TYPES: e.append(f"Concealment {c.get('id')} has invalid type")
            if float(c.get("base_concealment",0))<0: e.append(f"Concealment {c.get('id')} has negative base")
        for t in self.records["tracking_profiles"].values():
            if any(x not in TRAIL_TYPES for x in t.get("trail_types",[])): e.append(f"Tracking {t.get('id')} has invalid trail type")
        for snd in self.records["sound_profiles"].values():
            if int(snd.get("maximum_room_distance",0))>10: w.append(f"Sound {snd.get('id')} propagates far")
        return {"errors":e,"warnings":w}
    def get_sense_profile(self,actor_id:str|None=None): return self.records["actor_sense_profiles"].get("normal_humanoid_senses") or next(iter(self.records["actor_sense_profiles"].values()),{})
    def _room_env(self,room_id=""): return self.environment.resolve_room_environment({"id":room_id})
    def can_hide(self,actor_id,room_id=None):
        env=self._room_env(room_id or "")
        return {"ok": env["light"].get("light_class")!="blinding_placeholder", "environment":env}
    def attempt_hide(self,actor_id,profile_id=None,room_id=None,world_time=0):
        profile=self.records["concealment_profiles"].get(profile_id or "basic_hide") or {"id":profile_id or "basic_hide","base_concealment":25}
        check=self.can_hide(actor_id,room_id); score=float(profile.get("base_concealment",25))+float(profile.get("stationary_bonus",0))
        sid=self._id(self.world_id,"stealth",actor_id)
        self._audit(actor_id,"actor",actor_id,"hide_attempted","attempting",score,0,None,room_id,world_time,{})
        with sqlite3.connect(self.db_path) as c:
            row=c.execute("SELECT stealth_state_id,status FROM actor_stealth_state WHERE world_id=? AND actor_id=? AND status IN ('attempting','hidden','concealed','partially_revealed')",(self.world_id,actor_id)).fetchone()
            if row: return {"ok":True,"duplicate":True,"status":row[1],"stealth_state_id":row[0],"message":"You are already hidden."}
            c.execute("INSERT INTO actor_stealth_state(stealth_state_id,world_id,actor_id,concealment_profile_id,status,source_type,source_id,room_id,started_world_time,last_updated_world_time,concealment_score,revealed_to_json,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(sid,self.world_id,actor_id,profile.get("id"),"hidden" if check["ok"] else "broken","profile",profile.get("id"),room_id or "",world_time,world_time,score,"{}",_json({"environment":check["environment"]})))
        self._publish("actor_hidden" if check["ok"] else "actor_hide_failed",{"actor_id":actor_id,"stealth_state_id":sid})
        return {"ok":check["ok"],"status":"hidden" if check["ok"] else "broken","stealth_state_id":sid,"concealment_score":score,"message":"You blend into cover." if check["ok"] else "You cannot find enough cover."}
    def get_stealth_state(self,actor_id):
        with sqlite3.connect(self.db_path) as c:
            c.row_factory=sqlite3.Row; r=c.execute("SELECT * FROM actor_stealth_state WHERE world_id=? AND actor_id=? ORDER BY created_at DESC LIMIT 1",(self.world_id,actor_id)).fetchone()
            return dict(r) if r else None
    def break_hide(self,actor_id,reason="manual",world_time=0):
        st=self.get_stealth_state(actor_id)
        if not st: return {"ok":True,"status":"inactive"}
        with sqlite3.connect(self.db_path) as c: c.execute("UPDATE actor_stealth_state SET status='broken',last_updated_world_time=?,metadata_json=? WHERE stealth_state_id=?",(world_time,_json({"break_reason":reason}),st["stealth_state_id"]))
        self._publish("actor_concealment_broken",{"actor_id":actor_id,"reason":reason}); return {"ok":True,"status":"broken"}
    def trace_hide(self,actor_id): return {"state":self.get_stealth_state(actor_id),"senses":self.get_sense_profile(actor_id),"restart_safe":True}
    def _knowledge(self,observer,target_type,target_id,ktype,status,confidence,source_type="perception",source_id="",expires=None,world_time=0):
        kid=self._id(self.world_id,"knowledge",observer,target_type,target_id,ktype)
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT INTO actor_perception_knowledge(knowledge_id,world_id,observer_actor_id,target_type,target_id,knowledge_type,status,first_detected_world_time,last_detected_world_time,expires_world_time,source_type,source_id,confidence,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(world_id,observer_actor_id,target_type,target_id,knowledge_type) DO UPDATE SET status=excluded.status,last_detected_world_time=excluded.last_detected_world_time,confidence=excluded.confidence,updated_at=CURRENT_TIMESTAMP",(kid,self.world_id,observer,target_type,target_id,ktype,status,world_time,world_time,expires,source_type,source_id,confidence,"{}"))
        self._publish("perception_knowledge_created",{"observer_actor_id":observer,"target_type":target_type,"target_id":target_id,"status":status}); return kid
    def evaluate_actor_detection(self,observer_actor_id,target_actor_id,room_id=None,world_time=0):
        senses=self.get_sense_profile(observer_actor_id); st=self.get_stealth_state(target_actor_id); env=self._room_env(room_id or (st or {}).get("room_id", ""))
        score=float(senses.get("awareness_rating",10))+float(senses.get("hearing_rating",0))*0.2+float(senses.get("scent_rating",0))*0.1
        threshold=0 if not st or st.get("status") not in {"hidden","concealed","partially_revealed"} else float(st.get("concealment_score") or 25)
        result="identified" if score>=threshold+10 else "detected" if score>=threshold else "hint" if score>=threshold*0.6 else "not_detected"
        if result in {"detected","identified"}: self._knowledge(observer_actor_id,"actor",target_actor_id,"actor_presence",result,score/100,"detection",st.get("stealth_state_id") if st else "",None,world_time)
        self._audit(observer_actor_id,"actor",target_actor_id,"target_detected",result,score,threshold,None,room_id,world_time,{"environment":env})
        return {"result":result,"identified":result=="identified","score":score,"threshold":threshold,"environment":env}
    def reveal_to(self,observer,target_type,target_id,status="identified"):
        return self._knowledge(observer,target_type,target_id,"actor_presence" if target_type=="actor" else f"{target_type}_presence",status,1.0)
    def search_room(self,actor_id,room_id=None,search_type=None,world_time=0):
        self._publish("search_started",{"actor_id":actor_id,"room_id":room_id,"search_type":search_type or "general"})
        trails=self.find_tracks(actor_id,room_id)
        found=[]
        if trails: found.append("tracks")
        self._audit(actor_id,"room",room_id or "","search_completed","detected" if found else "not_detected",len(found),1,None,room_id,world_time,{})
        self._publish("search_completed",{"actor_id":actor_id,"room_id":room_id,"results":found})
        return {"ok":True,"results":found,"message":"You find signs of tracks." if found else "You search carefully but find nothing obvious."}
    def create_trail(self,trail_type,source_actor_id,room_id,from_room_id="",to_room_id="",direction="",strength=10,world_time=0,event_id=None,terrain_profile_id="dirt_traces"):
        event_id=event_id or self._id("trail_event",trail_type,source_actor_id,room_id,from_room_id,to_room_id,direction,world_time)
        tid=self._id(self.world_id,"trail",event_id,trail_type)
        env=self._room_env(room_id); expires=world_time+int((self.records["terrain_trace_profiles"].get(terrain_profile_id) or {}).get("footprint_retention",120))
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT OR IGNORE INTO sensory_trails(trail_id,world_id,trail_type,source_actor_id,source_type,source_id,room_id,from_room_id,to_room_id,direction,strength,created_world_time,expires_world_time,terrain_profile_id,weather_snapshot_json,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tid,self.world_id,trail_type,source_actor_id,"movement",event_id,room_id,from_room_id,to_room_id,direction,float(strength),world_time,expires,terrain_profile_id,_json(env.get("weather")),_json({"clues":{"direction":direction,"age_band":"fresh"}})))
        self._publish("trail_created",{"trail_id":tid,"trail_type":trail_type,"room_id":room_id}); return {"trail_id":tid,"event_id":event_id}
    def degrade_trails(self,world_time):
        with sqlite3.connect(self.db_path) as c:
            rows=c.execute("SELECT trail_id,strength,created_world_time,terrain_profile_id,weather_snapshot_json FROM sensory_trails WHERE world_id=?",(self.world_id,)).fetchall()
            for tid,strength,created,terr,wjson in rows:
                age=max(0,world_time-int(created or 0)); weather=json.loads(wjson or '{}'); factor=max(0.0,1-age/240)
                if float(weather.get("precipitation_intensity") or 0)>0.5: factor*=0.5
                c.execute("UPDATE sensory_trails SET age_minutes=?, strength=? WHERE trail_id=?",(age,float(strength)*factor,tid))
        return {"updated":len(rows)}
    def find_tracks(self,actor_id,room_id=None):
        with sqlite3.connect(self.db_path) as c:
            c.row_factory=sqlite3.Row; return [dict(r) for r in c.execute("SELECT * FROM sensory_trails WHERE world_id=? AND (? IS NULL OR room_id=?) AND strength>0 ORDER BY created_world_time DESC",(self.world_id,room_id,room_id)).fetchall()]
    def track_target(self,actor_id,target_ref="tracks",room_id=None,world_time=0):
        trails=self.find_tracks(actor_id,room_id); sid=self._id(self.world_id,"tracking",actor_id,target_ref)
        status="tracking" if trails else "lost"; last=trails[0]["trail_id"] if trails else ""
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT OR REPLACE INTO actor_tracking_sessions(tracking_session_id,actor_id,target_type,target_id,trail_type,status,current_room_id,last_trail_id,confidence,started_world_time,last_updated_world_time,expires_world_time,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(sid,actor_id,"trail",str(target_ref),trails[0]["trail_type"] if trails else "footprint",status,room_id or "",last,0.8 if trails else 0,world_time,world_time,world_time+120,_json({})))
        self._publish("tracking_started",{"actor_id":actor_id,"status":status}); return {"status":status,"trail":trails[0] if trails else None,"message":self.get_tracking_hint(actor_id,last)["message"] if trails else "You lose the trail."}
    def get_tracking_hint(self,actor_id,trail_id):
        with sqlite3.connect(self.db_path) as c:
            c.row_factory=sqlite3.Row; r=c.execute("SELECT * FROM sensory_trails WHERE trail_id=?",(trail_id,)).fetchone()
        if not r: return {"message":"No trackable trail remains."}
        d=dict(r); return {"message":f"Tracks lead {d.get('direction') or 'onward'}; they look recent.","trail":d}
    def emit_sound(self,profile_id,room_id,intensity=None,source_actor_id="",event_id=None,world_time=0):
        p=self.records["sound_profiles"].get(profile_id) or {"id":profile_id,"base_intensity":intensity or 5,"maximum_room_distance":1}
        event_id=event_id or self._id("sound",profile_id,room_id,source_actor_id,world_time); sid=self._id(self.world_id,"sound",event_id)
        inten=float(intensity if intensity is not None else p.get("base_intensity",5))
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT OR IGNORE INTO sensory_sound_events(sound_event_id,world_id,source_type,source_id,source_actor_id,origin_room_id,sound_profile_id,intensity,created_world_time,expires_world_time,event_id,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(sid,self.world_id,"actor" if source_actor_id else "room",source_actor_id or room_id,source_actor_id,room_id,profile_id,inten,world_time,world_time+5,event_id,_json({})))
        self._publish("sound_emitted",{"sound_event_id":sid,"room_id":room_id}); return {"sound_event_id":sid,"event_id":event_id,"profile":p}
    def hear_sound(self,actor_id,sound_event_id,distance=0,direction="nearby"):
        with sqlite3.connect(self.db_path) as c:
            c.row_factory=sqlite3.Row; r=c.execute("SELECT * FROM sensory_sound_events WHERE sound_event_id=?",(sound_event_id,)).fetchone()
        if not r: return {"result":"inaudible","message":"You hear nothing unusual."}
        d=dict(r); p=self.records["sound_profiles"].get(d["sound_profile_id"]) or {}; maxd=int(p.get("maximum_room_distance",1))
        result="inaudible" if distance>maxd else "faint" if distance==maxd else "audible" if distance else "clear"
        msg="You hear nothing unusual." if result=="inaudible" else f"You hear {result} {p.get('sound_type','sound')} to the {direction}."
        self._publish("sound_heard",{"actor_id":actor_id,"sound_event_id":sound_event_id,"result":result}); return {"result":result,"message":msg}
    def detect_scent(self,actor_id,room_id=None):
        trails=[t for t in self.find_tracks(actor_id,room_id) if t.get("trail_type") in {"scent","blood"}]
        if not trails: return {"result":"no_scent","message":"You catch no distinct scent."}
        strength=float(trails[0].get("strength") or 0); result="identified_scent" if strength>20 else "strong_scent" if strength>10 else "faint_scent"
        self._publish("scent_detected",{"actor_id":actor_id,"trail_id":trails[0]["trail_id"],"result":result}); return {"result":result,"message":"A scent trail lingers here.","trail":trails[0]}
    def conceal_item(self,item_instance_id,actor_id,room_id="",profile_id="concealed_item_basic",world_time=0):
        cid=self._id(self.world_id,"item",item_instance_id); prof=self.records["concealment_profiles"].get(profile_id) or {"base_concealment":15}
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT OR REPLACE INTO item_concealment_state(concealment_state_id,item_instance_id,room_id,concealed_by_actor_id,concealment_profile_id,concealment_score,status,created_world_time,metadata_json) VALUES(?,?,?,?,?,?,?,?,?)",(cid,item_instance_id,room_id,actor_id,profile_id,float(prof.get("base_concealment",15)),"hidden",world_time,"{}"))
        self._publish("item_concealed",{"item_instance_id":item_instance_id}); return {"ok":True,"concealment_state_id":cid}
    def _audit(self,observer,target_type,target_id,operation,result,score,threshold,source_event_id,room_id,world_time,metadata):
        aid=self._id(self.world_id,"audit",observer,target_type,target_id,operation,world_time,score,threshold)
        with sqlite3.connect(self.db_path) as c: c.execute("INSERT OR IGNORE INTO perception_audit_events(audit_event_id,world_id,observer_actor_id,target_type,target_id,operation,result,score,threshold,source_event_id,room_id,world_time,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(aid,self.world_id,observer,target_type,target_id,operation,result,score,threshold,source_event_id,room_id or "",world_time,_json(metadata)))
    def trace_detection(self,observer,target_type,target_id): return self.evaluate_actor_detection(observer,target_id) if target_type=="actor" else {"result":"not_detected"}
    def trace_search(self,actor_id,target): return {"search":target,"senses":self.get_sense_profile(actor_id),"environment":self._room_env("")}
    def trace_tracking(self,actor_id,target_ref): return {"target":target_ref,"tracks":self.find_tracks(actor_id)}
    def trace_sound(self,sound_event_id):
        with sqlite3.connect(self.db_path) as c: c.row_factory=sqlite3.Row; r=c.execute("SELECT * FROM sensory_sound_events WHERE sound_event_id=?",(sound_event_id,)).fetchone(); return dict(r) if r else {}
    def trace_trail(self,trail_id): return self.get_tracking_hint("",trail_id)
