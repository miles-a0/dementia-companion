import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
IMMICH_URL = os.getenv("IMMICH_URL", "http://immich-server:3001")
VIKUNJA_URL = os.getenv("VIKUNJA_URL", "http://vikunja:3456")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30