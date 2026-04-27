import os
import stripe
from fastapi import FastAPI, Request, Header, HTTPException
from src.payment_manager import PaymentManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StripeWebhook")

app = FastAPI()
payment_manager = PaymentManager()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handles Stripe Webhook events.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    payload = await request.body()

    try:
        # Verify the event came from Stripe
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract user_id from client_reference_id
        user_id = session.get('client_reference_id')
        
        # Extract package_id from metadata
        metadata = session.get('metadata', {})
        package_id = metadata.get('package_id')
        
        if user_id and package_id:
            payment_manager.fulfill_payment(user_id, package_id)
            logger.info(f"Successfully credited user {user_id} for package {package_id}")
        else:
            logger.error(f"Missing user_id or package_id in session: {user_id}, {package_id}")

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
