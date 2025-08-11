import os
from dotenv import load_dotenv

# Load .env if present to configure DB (PostgreSQL) and other secrets
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


