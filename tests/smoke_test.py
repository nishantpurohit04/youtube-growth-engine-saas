import os
from dotenv import load_dotenv
from src.youtube_client import YouTubeClient
from src.ai_strategist import AIStrategist
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

print("--- 🧪 Starting Smoke Test ---")

# 1. Test YouTube Client
try:
    yt = YouTubeClient()
    stats = yt.get_channel_stats("UC_x5XG1OV2s6VJPzS6L_ovw") 
    print("✅ YouTube API: Connection Successful")
except Exception as e:
    print(f"❌ YouTube API: Failed - {e}")

# 2. Test AI Strategist (Gemini)
try:
    ai = AIStrategist()
    res = ai.generate_growth_plan("Test summary for validation")
    print("✅ Gemini API: Connection Successful")
except Exception as e:
    print(f"❌ Gemini API: Failed - {e}")

# 3. Test Firebase/Firestore
try:
    if not firebase_admin._apps:
        cred_path = "service_account.json"
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase/Firestore: Connection Successful")
except Exception as e:
    print(f"❌ Firebase: Failed - {e}")

print("--- 🏁 Smoke Test Complete ---")
