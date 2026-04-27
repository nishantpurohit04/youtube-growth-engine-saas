import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import json
import re
import base64
from src.config import get_secret

logger = logging.getLogger("CreditManager")

class CreditManager:
    _db = None

    def __init__(self):
        self._initialize_firebase()
        self.db = CreditManager._db

    def _extract_pem(self, text):
        """Extracts a PEM block from a string, ignoring surrounding quotes or JSON noise."""
        pattern = r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0)
        return None

    def _initialize_firebase(self):
        """The ultimate fail-safe Firebase initializer."""
        try:
            if not firebase_admin._apps:
                secret = get_secret("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not secret:
                    logger.error("CRITICAL: FIREBASE_SERVICE_ACCOUNT_KEY missing.")
                    return

                # STRATEGY 1: Direct Dict / JSON Load
                try:
                    if isinstance(secret, dict):
                        cred_dict = secret
                    elif isinstance(secret, str) and secret.strip().startswith('{'):
                        cred_dict = json.loads(secret)
                    else:
                        raise ValueError("Not a dict or JSON string")
                    
                    if 'private_key' in cred_dict:
                        pk = cred_dict['private_key'].replace('\\n', '\n')
                        cred_dict['private_key'] = pk
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    CreditManager._db = firestore.client()
                    return
                except Exception as e1:
                    logger.warning(f"Strategy 1 (JSON) failed: {e1}")

                # STRATEGY 2: PEM Extraction (Regex)
                try:
                    pem_key = self._extract_pem(str(secret))
                    if pem_key:
                        # We need a full dict for Certificate, so we create a dummy one 
                        # if we only have the key. This is risky but sometimes works.
                        # Better yet, if we have the secret string, we try to find the other fields.
                        if isinstance(secret, str) and '{' in secret:
                            # Try to rebuild the dict from the string but with the repaired key
                            d = json.loads(secret)
                            d['private_key'] = pem_key
                            cred = credentials.Certificate(d)
                            firebase_admin.initialize_app(cred)
                            CreditManager._db = firestore.client()
                            return
                except Exception as e2:
                    logger.warning(f"Strategy 2 (PEM) failed: {e2}")

                # STRATEGY 3: Base64 Fallback (common for cloud secrets)
                try:
                    # If the secret looks like base64, decode it
                    if isinstance(secret, str) and len(secret) > 100 and '=' in secret:
                        decoded = base64.b64decode(secret).decode('utf-8')
                        if '{' in decoded:
                            d = json.loads(decoded)
                            if 'private_key' in d:
                                d['private_key'] = d['private_key'].replace('\\n', '\n')
                            cred = credentials.Certificate(d)
                            firebase_admin.initialize_app(cred)
                            CreditManager._db = firestore.client()
                            return
                except Exception as e3:
                    logger.warning(f"Strategy 3 (Base64) failed: {e3}")

                logger.error("All Firebase initialization strategies failed.")
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
            logger.error(f"Error retrieving credits for {user_id}: {e}")
            return f"ERROR: {str(e)}"

    def initialize_user_credits(self, user_id, initial_amount=5):
        if not self.db: return None
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.set({"credit_balance": initial_amount, "created_at": firestore.firestore.SERVER_TIMESTAMP}, merge=True)
            return initial_amount
        except Exception as e:
            logger.error(f"Error initializing credits for {user_id}: {e}")
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
            logger.error(f"Error deducting credit for {user_id}: {e}")
            return False, 0

    def add_credits(self, user_id, amount):
        if not self.db: return False
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.update({"credit_balance": firestore.firestore.Increment(amount)})
            return True
        except Exception as e:
            logger.error(f"Error adding credits for {user_id}: {e}")
            return False
