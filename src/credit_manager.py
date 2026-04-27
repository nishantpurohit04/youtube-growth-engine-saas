import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from src.firebase_init import initialize_firebase_admin

logger = logging.getLogger("CreditManager")

class CreditManager:
    def __init__(self):
        self.db = initialize_firebase_admin()

    def get_user_credits(self, user_id):
        if not self.db:
            # One last attempt to init
            self.db = initialize_firebase_admin()
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
        if not self.db: return None
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
