import os
import stripe
from src.credit_manager import CreditManager
import logging

logger = logging.getLogger("PaymentManager")

# Load Stripe API Key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Credit Packages Configuration
# format: package_id: (amount_in_inr, credit_count)
CREDIT_PACKAGES = {
    "starter": (5, 50),
    "growth": (15, 200),
    "pro": (30, 500)
}

class PaymentManager:
    def __init__(self):
        self.credit_manager = CreditManager()

    def create_checkout_session(self, user_id, package_id):
        """
        Creates a Stripe Checkout session for a specific credit package.
        """
        if package_id not in CREDIT_PACKAGES:
            raise ValueError("Invalid package ID")

        price, credits = CREDIT_PACKAGES[package_id]

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{package_id.capitalize()} Pack - {credits} Credits",
                            'description': "Add credits to your YouTube Growth Engine account.",
                        },
                        'unit_amount': price * 100, # Stripe expects amount in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                # Pass the user_id in metadata so the webhook knows who to credit
                client_reference_id=user_id,
                metadata={
                    'package_id': package_id
                },
                success_url="https://your-app-url.streamlit.app/?success=true",
                cancel_url="https://your-app-url.streamlit.app/?canceled=true",
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe Session Error: {str(e)}")
            return None

    def fulfill_payment(self, user_id, package_id):
        """
        Adds credits to the user's balance after a successful payment.
        Called by the webhook.
        """
        if package_id not in CREDIT_PACKAGES:
            logger.error(f"Payment fulfillment failed: Invalid package {package_id}")
            return False
        
        credits = CREDIT_PACKAGES[package_id][1]
        success = self.credit_manager.add_credits(user_id, credits)
        
        if success:
            logger.info(f"Payment fulfilled: Added {credits} credits to user {user_id}")
        else:
            logger.error(f"Payment fulfillment failed for user {user_id}")
            
        return success
