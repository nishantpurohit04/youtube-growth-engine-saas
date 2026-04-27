import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import json
import tempfile
from src.config import get_secret

logger = logging.getLogger("FirebaseInit")

def initialize_firebase_admin():
    """
    Centralized, Nuclear-Option Firebase Initializer.
    Bypasses all common Cloud/Streamlit formatting issues.
    """
    try:
        if not firebase_admin._apps:
            secret = get_secret("FIREBASE_SERVICE_ACCOUNT_KEY")
            if not secret:
                logger.error("CRITICAL: FIREBASE_SERVICE_ACCOUNT_KEY missing.")
                return None

            # 1. Get a clean dictionary
            if isinstance(secret, dict):
                cred_dict = secret
            elif isinstance(secret, str) and secret.strip().startswith('{'):
                try:
                    cred_dict = json.loads(secret)
                except json.JSONDecodeError as e:
                    logger.error(f"CRITICAL: Invalid JSON: {e}")
                    return None
            else:
                # Assume it's a path
                try:
                    cred = credentials.Certificate(secret)
                    firebase_admin.initialize_app(cred)
                    return firestore.client()
                except Exception as e:
                    logger.error(f"Path-based load failed: {e}")
                    return None

            # 2. NUCLEAR SANITIZATION of the private key
            if 'private_key' in cred_dict:
                pk = cred_dict['private_key']
                if isinstance(pk, str):
                    # Remove accidental surrounding quotes
                    pk = pk.strip().strip('"').strip("'")
                    # Fix Windows-style carriage returns
                    pk = pk.replace('\\r\\n', '\n').replace('\\r', '')
                    # Fix escaped newlines (the most common Streamlit issue)
                    pk = pk.replace('\\n', '\n')
                    # Final trim
                    pk = pk.strip()
                    cred_dict['private_key'] = pk
            
            # 3. TEMPORARY FILE BYPASS (The most stable method)
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tf:
                    json.dump(cred_dict, tf)
                    temp_path = tf.name
                
                cred = credentials.Certificate(temp_path)
                firebase_admin.initialize_app(cred)
                os.remove(temp_path)
                logger.info("Firebase initialized successfully via Nuclear TempFile bypass.")
            except Exception as e:
                logger.error(f"TempFile bypass failed: {e}. Trying direct dict...")
                # Final fallback
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)

        return firestore.client()
    except Exception as e:
        logger.error(f"Firebase Admin critical failure: {str(e)}")
        return None
