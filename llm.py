import json,requests,time
from config import API_KEY,MODEL,VISION_MODEL
URL='https://openrouter.ai/api/v1/chat/completions'
SYSTEM='''You are an AI browser agent planner. Return exactly ONE JSON action. Allowed: open(url), click(selector), type(selector,text), press(key), scroll(direction,amount), wait(seconds), extract(selector), verify, done(message). Use the current DOM/visual evidence. Prefer supplied selectors. If an action failed, change strategy. Never claim completion without evidence.'''
SCHEMA={'type':'object','properties':{'action':{'type':'string','enum':['open','click','type','press','scroll','wait','extract','verify','done']},'url':{'type':'string'},'selector':{'type':'string'},'text':{'type':'string'},'key':{'type':'string'},'direction':{'type':'string'},'amount':{'type':'number'},'seconds':{'type':'number'},'message':{'type':'string'},'reason':{'type':'string'}},'required':['action'],'additionalProperties':False}
def headers(): return {'Authorization':f'Bearer {API_KEY}','Content-Type':'application/json'}
def request(body,timeout):
    for attempt in range(3):
     r=requests.post(URL,headers=headers(),json=body,timeout=timeout)
     if r.status_code != 402 or attempt == 2:break
     time.sleep(2)
    if not r.ok:
        try: detail=r.json().get('error',{}).get('message',r.text)
        except ValueError: detail=r.text
        raise RuntimeError(f'OpenRouter request failed ({r.status_code}): {detail}')
    return r.json()
def parse(x):
    if isinstance(x,list): x=''.join(i.get('text','') for i in x if isinstance(i,dict))
    text=x.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
    start=text.find('{')
    end=text.rfind('}')
    if start < 0 or end < start:
        raise ValueError('LLM response did not contain a JSON object')
    return json.loads(text[start:end + 1])
def planner(task,state,history):
    if not API_KEY: raise RuntimeError('OPENROUTER_API_KEY is not configured')
    body={'model':MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'task':task,'state':state,'history':history[-4:]},separators=(',',':'))}],'temperature':.1,'max_tokens':300,'response_format':{'type':'json_schema','json_schema':{'name':'action','strict':True,'schema':SCHEMA}}}
    try:
        return parse(request(body,60)['choices'][0]['message']['content'])
    except (json.JSONDecodeError,ValueError):
        body['temperature']=0
        body['messages'].append({'role':'user','content':'Return one complete JSON object only. Do not use markdown.'})
        return parse(request(body,60)['choices'][0]['message']['content'])
def vision(task,state,img):
    body={'model':VISION_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':f'Task: {task}. Analyze screenshot. Return JSON with visual_summary, useful_targets, completion_evidence.'},{'type':'image_url','image_url':{'url':f'data:image/png;base64,{img}'}}]}],'temperature':.1,'max_tokens':150}
    return parse(request(body,90)['choices'][0]['message']['content'])
def verify(task,state):
    body={'model':MODEL,'messages':[{'role':'system','content':'Return JSON only: {"completed":boolean,"confidence":number,"evidence":string}. Be strict; require evidence.'},{'role':'user','content':json.dumps({'task':task,'state':state})}],'temperature':0,'max_tokens':120,'response_format':{'type':'json_schema','json_schema':{'name':'verification','strict':True,'schema':{'type':'object','properties':{'completed':{'type':'boolean'},'confidence':{'type':'number'},'evidence':{'type':'string'}},'required':['completed','confidence','evidence'],'additionalProperties':False}}}}
    return parse(request(body,60)['choices'][0]['message']['content'])
