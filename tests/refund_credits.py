
from src.credit_manager import CreditManager
cm = CreditManager()
# We need to find the user_id. Since we don't have the session, 
# we'll search the 'users' collection for the most recent user or a known test user.
# For now, let's just implement a function that we can call or a loop.
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
users = db.collection('users').stream()
for user in users:
    uid = user.id
    cm.add_credits(uid, 50)
    print(f"Refunded 50 credits to {uid}")
