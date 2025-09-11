"""
Configuration module for the AdultingOS backend.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Server configuration
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8001"))

# Database configuration (for future implementation)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Feature flags
ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "False").lower() in ("true", "1", "t")
