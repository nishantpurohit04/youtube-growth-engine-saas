import firebase_admin
from firebase_admin import credentials, firestore
import logging
import json
from src.config import get_secret
from src.firebase_secrets import ENCRYPTED_FIREBASE_JSON
from cryptography.fernet import Fernet

logger = logging.getLogger("FirebaseInit")

def initialize_firebase_admin():
    """
    Mastermind Firebase Initializer.
    Decrypts the hardcoded blob using a key from Streamlit Secrets.
    """
    try:
        if not firebase_admin._apps:
            # 1. Fetch decryption key from secrets
            decryption_key = get_secret("FIREBASE_DECRYPTION_KEY")
            if not decryption_key:
                logger.error("CRITICAL: FIREBASE_DECRYPTION_KEY missing from secrets.")
                return None
            
            try:
                # 2. Decrypt the blob
                cipher_suite = Fernet(decryption_key.encode())
                decrypted_json_bytes = cipher_suite.decrypt(ENCRYPTED_FIREBASE_JSON.encode())
                cred_dict = json.loads(decrypted_json_bytes)
                
                # 3. Initialize Firebase
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully via Mastermind Decryption.")
            except Exception as e:
                logger.error(f"Decryption or Initialization failed: {e}")
                return None
        
        return firestore.client()
    except Exception as e:
        logger.error(f"Firebase Admin critical failure: {str(e)}")
        return None
