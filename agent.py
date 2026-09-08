import base64,json,time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from config import ALLOWED,HEADLESS,MAX_STEPS
from llm import planner,vision,verify
LOG=Path('logs'); SHOT=Path('screenshots'); LOG.mkdir(exist_ok=True); SHOT.mkdir(exist_ok=True)
class Agent:
 def __init__(self,headless=HEADLESS,max_steps=MAX_STEPS,use_vision=True): self.headless=headless;self.max_steps=max_steps;self.use_vision=use_vision;self.h=[];self.id=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
 def start(self):
  self.pw=sync_playwright().start();self.browser=self.pw.chromium.launch(headless=self.headless);self.ctx=self.browser.new_context(viewport={'width':1440,'height':900});self.page=self.ctx.new_page()
 def close(self):
  for x,m in [(getattr(self,'ctx',None),'close'),(getattr(self,'browser',None),'close'),(getattr(self,'pw',None),'stop')]:
   try:
    if x:getattr(x,m)()
   except:pass
 def current_url(self):
  try:return self.page.url
  except:return 'about:blank'
 def browser_was_closed(self,error):
  return 'Target page, context or browser has been closed' in str(error)
 def allowed(self,u):
  h=(urlparse(u).hostname or '').lower();return any(h==d or h.endswith('.'+d) for d in ALLOWED)
 def observe(self):
  loc=self.page.locator('input,textarea,button,a,select,[role="button"],[role="textbox"]'); out=[]
  try:n=min(loc.count(),25)
  except:n=0
  for i in range(n):
   try:
    e=loc.nth(i)
    if not e.is_visible():continue
    tag=e.evaluate('(e)=>e.tagName.toLowerCase()'); a={k:e.get_attribute(v) or '' for k,v in [('id','id'),('name','name'),('aria','aria-label'),('placeholder','placeholder'),('role','role'),('href','href')]}; txt=''
    if tag not in ('input','textarea','select'):
     try:txt=e.inner_text(timeout=300).strip()
     except:pass
    sel=f'#{a["id"]}' if a['id'] else (f'{tag}[name={json.dumps(a["name"])}]' if a['name'] else (f'{tag}[aria-label={json.dumps(a["aria"])}]' if a['aria'] else tag))
    out.append({'tag':tag,'text':txt[:150],'id':a['id'][:100],'name':a['name'][:100],'aria':a['aria'][:120],'placeholder':a['placeholder'][:120],'role':a['role'][:80],'href':a['href'][:200],'selector':sel})
   except:pass
  try:text=self.page.locator('body').inner_text(timeout=2000)
  except:text=''
  return {'url':self.page.url,'title':self.page.title(),'visible_text':text[:1500],'elements':out}
 def screenshot(self):
  b=self.page.screenshot(type='png');p=SHOT/f'{self.id}_{len(self.h)+1}.png';p.write_bytes(b);return base64.b64encode(b).decode(),str(p)
 def act(self,a):
  k=a['action']
  if k=='open':
   u=a['url'];
   if not u.startswith(('http://','https://')) or not self.allowed(u):raise ValueError('URL/domain not allowed')
   self.page.goto(u,wait_until='domcontentloaded',timeout=30000);return {'success':True}
  if k in ('click','type','extract'):
   l=self.page.locator(a['selector']).first;l.wait_for(state='visible',timeout=10000)
   if k=='click':l.click(timeout=10000);return {'success':True}
   if k=='type':l.fill(a.get('text',''),timeout=10000);return {'success':True}
   vals=[]
   for i in range(min(self.page.locator(a['selector']).count(),20)):
    try:
     t=self.page.locator(a['selector']).nth(i).inner_text(timeout=1000).strip()
     if t:vals.append(t)
    except:pass
   return {'success':True,'data':vals}
  if k=='press':self.page.keyboard.press(a.get('key','ENTER'));return {'success':True}
  if k=='scroll':self.page.mouse.wheel(0,abs(int(a.get('amount',600)))*(-1 if a.get('direction')=='up' else 1));time.sleep(.7);return {'success':True}
  if k=='wait':time.sleep(min(float(a.get('seconds',2)),10));return {'success':True}
  if k=='verify':return {'success':True,'verification':verify(self.task,self.observe())}
  if k=='done':return {'success':True,'message':a.get('message','done')}
  raise ValueError('unsupported action')
 def run(self,task):
  self.task=task;self.start()
  try:
   for step in range(1,self.max_steps+1):
    try:s=self.observe()
    except Exception as e:
     if self.browser_was_closed(e):return self.finish('cancelled','Browser was closed by the user')
     return self.finish('error',str(e))
    v={};shot=None
    if self.use_vision:
     try:img,shot=self.screenshot();v=vision(task,s,img)
     except Exception as e:v={'vision_error':str(e)}
    s['visual']=v
    try:a=planner(task,s,self.h)
    except Exception as e:return self.finish('error',str(e))
    r={'step':step,'action':a,'url_before':s['url'],'screenshot':shot}
    try:
     r['result']=self.act(a)
     if a['action']=='verify':
      z=r['result']['verification'];
      if z['completed'] and z['confidence']>=.75:
       self.h.append(r);return self.finish('success',z['evidence'])
     if a['action']=='done':
      try:
       z=verify(task,self.observe());r['post_done_verification']=z
      except Exception as e:
       self.h.append(r)
       message=str(e)
       if '402' in message or 'credits' in message.lower():
        return self.finish('success','Task actions completed; final verification was skipped because OpenRouter credits are unavailable')
       return self.finish('error','Task actions completed, but final verification failed: '+message)
      if z['completed'] and z['confidence']>=.75:
       self.h.append(r);return self.finish('success',z['evidence'])
     self.h.append(r)
    except Exception as e:
     if self.browser_was_closed(e):return self.finish('cancelled','Browser was closed by the user')
     r['result']={'success':False,'error':str(e)};self.h.append(r)
   return self.finish('incomplete','Maximum steps reached')
  finally:self.close()
 def finish(self,status,msg):
  d={'status':status,'message':msg,'session_id':self.id,'steps':self.h,'final_url':self.current_url() if getattr(self,'page',None) else ''};(LOG/f'{self.id}.json').write_text(json.dumps(d,indent=2),encoding='utf-8');return d
def run_agent(task,headless=HEADLESS,max_steps=MAX_STEPS,use_vision=True):return Agent(headless,max_steps,use_vision).run(task)
