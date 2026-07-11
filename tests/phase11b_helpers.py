from pathlib import Path
from engine.perception import PerceptionService

def svc(tmp_path):
    return PerceptionService(tmp_path/'perception.db', Path('worlds/shattered_realms'), 'shattered_realms')
