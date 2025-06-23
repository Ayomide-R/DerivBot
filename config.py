from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

APP_ID = os.getenv("APP_ID")
API_TOKEN = os.getenv("API_TOKEN")
MARKET = os.getenv("MARKET")