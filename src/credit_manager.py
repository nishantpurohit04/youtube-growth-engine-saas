import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import json
import re
from src.config import get_secret

logger = logging.getLogger("CreditManager")

class CreditManager:
    _db = None  # Singleton pattern for Firestore client

    def __init__(self):
        self._initialize_firebase()
        self.db = CreditManager._db

    def _clean_pem_key(self, key):
        """Aggressively cleans a PEM private key to ensure it's valid for the cryptography library."""
        if not key or not isinstance(key, str):
            return key
        
        # 1. Remove any surrounding quotes that might have been captured from a JSON string
        key = key.strip().strip('"').strip("'")
        
        # 2. Replace escaped newlines with actual newlines
        key = key.replace('\\n', '\n')
        
        # 3. Ensure the key starts and ends with the correct PEM boundaries
        # If it's missing the headers but contains 'BEGIN PRIVATE KEY', we wrap it.
        if "BEGIN PRIVATE KEY" in key and not key.startswith("-----BEGIN PRIVATE KEY-----"):
            # Find the start of the key and trim everything before it
            start_idx = key.find("BEGIN PRIVATE KEY")
            key = "-----" + key[start_idx:]
        
        if "END PRIVATE KEY" in key and not key.endswith("-----END PRIVATE KEY-----"):
            # Find the end of the key and trim everything after it
            end_idx = key.find("END PRIVATE KEY") + 18
            key = key[:end_idx] + "-----"
            
        return key

    def _initialize_firebase(self):
        """Robustly initializes Firebase Admin SDK using Cloud-Aware secrets with PEM repair."""
        try:
            if not firebase_admin._apps:
                secret = get_secret("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not secret:
                    logger.error("CRITICAL: FIREBASE_SERVICE_ACCOUNT_KEY is missing.")
                    return

                # Handle Case A: Secret is already a dictionary (Streamlit TOML)
                if isinstance(secret, dict):
                    cred_dict = secret
                # Handle Case B: Secret is a JSON string
                elif isinstance(secret, str) and secret.strip().startswith('{'):
                    try:
                        cred_dict = json.loads(secret)
                    except json.JSONDecodeError as e:
                        logger.error(f"CRITICAL: Secret is not valid JSON: {e}")
                        return
                # Handle Case C: Secret is a path to a file
                else:
                    cred_path = secret if os.path.exists(secret) else os.path.join(os.getcwd(), secret)
                    try:
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred)
                        CreditManager._db = firestore.client()
                        return
                    except Exception as e:
                        logger.error(f"File-based cred load failed: {e}")
                        return

                # Now process the dictionary (Case A & B)
                if 'private_key' in cred_dict:
                    cred_dict['private_key'] = self._clean_pem_key(cred_dict['private_key'])
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            
            CreditManager._db = firestore.client()
            logger.info("Firestore initialized successfully.")
        except Exception as e:
            logger.error(f"Firebase Admin initialization failed: {str(e)}")

    def get_user_credits(self, user_id):
        """Returns current credit balance; initializes new users with 5 credits."""
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
            return None

    def initialize_user_credits(self, user_id, initial_amount=5):
        """Sets up a new user document with initial free credits."""
        if not self.db:
            return None
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.set({
                "credit_balance": initial_amount,
                "created_at": firestore.firestore.SERVER_TIMESTAMP
            }, merge=True)
            return initial_amount
        except Exception as e:
            logger.error(f"Error initializing credits for {user_id}: {e}")
            return None

    def deduct_credit(self, user_id):
        """Decrements the user's credit balance by 1 using a transaction."""
        if not self.db:
            return False, 0
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
        """Adds credits to the user's balance."""
        if not self.db:
            return False
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.update({"credit_balance": firestore.firestore.Increment(amount)})
            return True
        except Exception as e:
            logger.error(f"Error adding credits for {user_id}: {e}")
            return False
