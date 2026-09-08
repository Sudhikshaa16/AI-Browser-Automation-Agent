import json,statistics
from pathlib import Path
L=list(Path('logs').glob('*.json'))
def metrics():
 if not L:return {'runs':0,'completion_rate':0,'avg_steps':0,'action_failure_rate':0}
 ds=[json.loads(p.read_text()) for p in L];a=sum(len(x.get('steps',[])) for x in ds);f=sum(not s.get('result',{}).get('success',True) for x in ds for s in x.get('steps',[]));return {'runs':len(ds),'completion_rate':round(sum(x.get('status')=='success' for x in ds)/len(ds),3),'avg_steps':round(statistics.mean([len(x.get('steps',[])) for x in ds]),2),'action_failure_rate':round(f/a,3) if a else 0}
