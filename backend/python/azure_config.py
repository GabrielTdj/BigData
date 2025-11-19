import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Azure CLU (Conversational Language Understanding)
CLU_PROJECT_NAME = os.getenv('CLU_PROJECT_NAME')
CLU_DEPLOYMENT_NAME = os.getenv('CLU_DEPLOYMENT_NAME', 'production')
CLU_ENDPOINT = os.getenv('CLU_ENDPOINT')
CLU_KEY = os.getenv('CLU_KEY')

# Text Analytics
TEXT_ANALYTICS_ENDPOINT = os.getenv('TEXT_ANALYTICS_ENDPOINT')
TEXT_ANALYTICS_KEY = os.getenv('TEXT_ANALYTICS_KEY')

# Amadeus
AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID')
AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')

# Cosmos DB
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE = os.getenv('COSMOS_DATABASE', 'chatbotdb')
COSMOS_CONTAINER = os.getenv('COSMOS_CONTAINER', 'conversations')

# App
PORT = int(os.getenv('PORT', 5000))
