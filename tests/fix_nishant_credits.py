
from src.credit_manager import CreditManager
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    import json
    secret = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)

cm = CreditManager()
user_id = "BIRFWuEoNQP7XIKbCr7RJzTkM1T2"

success = cm.add_credits(user_id, 50)
if success:
    print(f"✅ SUCCESS: Added 50 credits to {user_id}. Current balance updated.")
else:
    print(f"❌ FAILED: Could not add credits to {user_id}.")
