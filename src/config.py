import os
from dotenv import load_dotenv

def load_env_config():
    """Ensures .env is loaded from the absolute project root."""
    env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path=env_path)

def get_env_clean(key):
    """Fetches env var and strips quotes/whitespace."""
    val = os.getenv(key, "")
    return val.strip().strip('"').strip("'")
