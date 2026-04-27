
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize firebase if not already
if not firebase_admin._apps:
    import json
    secret = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    if secret.strip().startswith('{'):
        import json
        cred_dict = json.loads(secret)
        if 'private_key' in cred_dict:
            cred_dict['private_key'] = cred_dict['private_key'].replace('\n', '\n')
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("--- 📋 FIRESTORE USER AUDIT ---")
users = db.collection('users').stream()
found_users = []
for user in users:
    found_users.append({"id": user.id, "data": user.to_dict()})

if not found_users:
    print("No users found in the 'users' collection.")
else:
    for u in found_users:
        print(f"User ID: {u['id']} | Balance: {u['data'].get('credit_balance', 'N/A')}")

print("------------------------------")
