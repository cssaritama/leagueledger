import os

APP_NAME = "LeagueLedger API"
APP_VERSION = "1.0.2"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leagueledger.db")

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:8080,http://127.0.0.1:8080"
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]

AUTO_CREATE_SCHEMA = os.getenv("AUTO_CREATE_SCHEMA", "true").lower() in {"1", "true", "yes"}
