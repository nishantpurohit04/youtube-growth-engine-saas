import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

logger = logging.getLogger("CreditManager")

class CreditManager:
    def __init__(self):
        self.db = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            # Check if firebase_admin is already initialized to avoid ValueError
            if not firebase_admin._apps:
                secret = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not secret:
                    logger.warning("FIREBASE_SERVICE_ACCOUNT_KEY not found. Firestore will be unavailable.")
                    return
                
                import json
                # If the secret looks like a JSON string, load it as a dict
                if secret.strip().startswith('{'):
                    try:
                        cred_dict = json.loads(secret)
                        cred = credentials.Certificate(cred_dict)
                    except json.JSONDecodeError:
                        logger.error("FIREBASE_SERVICE_ACCOUNT_KEY is not valid JSON.")
                        return
                else:
                    # Otherwise, treat it as a path to a .json file
                    cred = credentials.Certificate(secret)
                
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("Firestore initialized successfully.")
        except Exception as e:
            logger.error(f"Firebase Admin initialization failed: {str(e)}")

    def get_user_credits(self, user_id):
        """Returns the current credit balance for a user."""
        if not self.db:
            return None
        
        try:
            user_ref = self.db.collection("users").document(user_id)
            doc = user_ref.get()
            if doc.exists:
                return doc.to_dict().get("credit_balance", 0)
            else:
                # User doesn't exist in Firestore, initialize them with free credits
                return self.initialize_user_credits(user_id)
        except Exception as e:
            logger.error(f"Error fetching credits for {user_id}: {str(e)}")
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
            logger.info(f"Initialized {initial_amount} free credits for user {user_id}.")
            return initial_amount
        except Exception as e:
            logger.error(f"Error initializing credits for {user_id}: {str(e)}")
            return None

    def deduct_credit(self, user_id):
        """Decrements the user's credit balance by 1."""
        if not self.db:
            return False
        
        try:
            user_ref = self.db.collection("users").document(user_id)
            
            # Use a transaction to ensure atomic updates (prevent race conditions)
            @firestore.transactional
            def update_in_transaction(transaction, ref):
                snapshot = ref.get(transaction=transaction)
                balance = snapshot.get("credit_balance") if snapshot.exists else 0
                if balance >= 1:
                    transaction.update(ref, {"credit_balance": balance - 1})
                    return True
                return False

            transaction = self.db.transaction()
            success = update_in_transaction(transaction, user_ref)
            
            if success:
                logger.info(f"Deducted 1 credit from user {user_id}.")
            else:
                logger.warning(f"Insufficient credits for user {user_id}.")
            
            return success
        except Exception as e:
            logger.error(f"Error deducting credit for {user_id}: {str(e)}")
            return False

    def add_credits(self, user_id, amount):
        """Adds a specified number of credits to the user's balance."""
        if not self.db:
            return False
        
        try:
            user_ref = self.db.collection("users").document(user_id)
            user_ref.update({
                "credit_balance": firestore.firestore.Increment(amount)
            })
            logger.info(f"Added {amount} credits to user {user_id}.")
            return True
        except Exception as e:
            logger.error(f"Error adding credits for {user_id}: {str(e)}")
            return False
