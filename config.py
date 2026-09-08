import os
from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv('OPENROUTER_API_KEY',''); MODEL=os.getenv('OPENROUTER_MODEL','minimax/minimax-m3:free')
VISION_MODEL=os.getenv('OPENROUTER_VISION_MODEL','minimax/minimax-m3:free')
MAX_STEPS=int(os.getenv('MAX_STEPS','15')); HEADLESS=os.getenv('HEADLESS','false').lower()=='true'
ALLOWED={x.strip().lower() for x in os.getenv('ALLOWED_DOMAINS','youtube.com,wikipedia.org,google.com,amazon.com').split(',') if x.strip()}
