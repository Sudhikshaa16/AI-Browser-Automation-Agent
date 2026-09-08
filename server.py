from fastapi import FastAPI,HTTPException
from threading import Lock
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from fastapi.responses import FileResponse
from agent import run_agent
from evaluator import metrics
from config import MAX_STEPS,HEADLESS
app=FastAPI(title='AI Browser Automation Agent',version='3.0')
AGENT_LOCK=Lock()
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
class Command(BaseModel):
 query:str=Field(...,min_length=2);headless:bool=HEADLESS;max_steps:int=Field(MAX_STEPS,ge=1,le=30);use_vision:bool=True
@app.get('/')
def home():return FileResponse('static/index.html')
@app.get('/health')
def health():return {'status':'healthy'}
@app.get('/metrics')
def met():return metrics()
@app.post('/command')
def command(c:Command):
 try:
  with AGENT_LOCK:return run_agent(c.query,c.headless,c.max_steps,c.use_vision)
 except Exception as e:raise HTTPException(500,str(e))
