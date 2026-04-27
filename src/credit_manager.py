import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import json
import tempfile
from src.config import get_secret

logger = logging.getLogger("CreditManager")

class CreditManager:
    _db = None

    def __init__(self):
        self._initialize_firebase()
        self.db = CreditManager._db

    def _initialize_firebase(self):
        """The Ultimate Robust Initializer: Uses Temporary Files to bypass dict-loading bugs."""
        try:
            if not firebase_admin._apps:
                secret = get_secret("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not secret:
                    logger.error("CRITICAL: FIREBASE_SERVICE_ACCOUNT_KEY missing.")
                    return

                # 1. Handle the secret to get a valid dictionary
                if isinstance(secret, dict):
                    cred_dict = secret
                elif isinstance(secret, str) and secret.strip().startswith('{'):
                    try:
                        cred_dict = json.loads(secret)
                    except json.JSONDecodeError as e:
                        logger.error(f"CRITICAL: Invalid JSON: {e}")
                        return
                else:
                    # It's already a path
                    try:
                        cred = credentials.Certificate(secret)
                        firebase_admin.initialize_app(cred)
                        CreditManager._db = firestore.client()
                        return
                    except Exception as e:
                        logger.error(f"File load failed: {e}")
                        return

                # 2. Sanitize the private key
                if 'private_key' in cred_dict:
                    pk = cred_dict['private_key']
                    pk = pk.replace('\\n', '\n').strip('"').strip("'")
                    cred_dict['private_key'] = pk

                # 3. THE BYPASS: Write to a temporary file
                # This is the most stable way to initialize firebase-admin in the cloud
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tf:
                        json.dump(cred_dict, tf)
                        temp_path = tf.name
                    
                    cred = credentials.Certificate(temp_path)
                    firebase_admin.initialize_app(cred)
                    # Clean up the temp file immediately after initialization
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Temporary file bypass failed: {e}")
                    # Fallback to direct dict if file fails
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
            
            CreditManager._db = firestore.client()
            logger.info("Firestore initialized successfully via TempFile bypass.")
        except Exception as e:
            logger.error(f"Firebase Admin critical failure: {str(e)}")

    def get_user_credits(self, user_id):
        if not self.db:
            self._initialize_firebase()
            self.db = CreditManager._db
            if not self.db:
                return None
        try:
            user_ref = self.db.collection("users").document(user_id)
            doc = user_ref.get()
            if doc.exists:
                return doc.to_dict().get("credit_balance", 0)
            user_ref.set({"credit_balance": 5})
            return 5
        except Exception as e:
            logger.error(f"Error retrieving credits: {e}")
            return None

    def initialize_user_credits(self, user_id, initial_amount=5):
        if not self.db: return None
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.set({"credit_balance": initial_amount, "created_at": firestore.firestore.SERVER_TIMESTAMP}, merge=True)
            return initial_amount
        except Exception as e:
            logger.error(f"Error initializing credits: {e}")
            return None

    def deduct_credit(self, user_id):
        if not self.db: return False, 0
        try:
            user_ref = self.db.collection("users").document(user_id)
            @firestore.transactional
            def update_in_transaction(transaction, ref):
                snapshot = ref.get(transaction=transaction)
                balance = snapshot.get("credit_balance") if snapshot.exists else 0
                if balance >= 1:
                    new_balance = balance - 1
                    transaction.update(ref, {"credit_balance": new_balance})
                    return True, new_balance
                return False, balance
            transaction = self.db.transaction()
            return update_in_transaction(transaction, user_ref)
        except Exception as e:
            logger.error(f"Error deducting credit: {e}")
            return False, 0

    def add_credits(self, user_id, amount):
        if not self.db: return False
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.update({"credit_balance": firestore.firestore.Increment(amount)})
            return True
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return False
