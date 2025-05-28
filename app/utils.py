import os
from dotenv import load_dotenv
import json


load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_KEY not set in .env")

# BASE_DIR = the parent folder of this utils.py file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def prettify_output(text):

    output = ''
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    for key in data:
        
        output += str(key).capitalize().replace('_', ' ')
        output += ': \n'
        output += str(data[key])
        output += '\n \n'

    return output