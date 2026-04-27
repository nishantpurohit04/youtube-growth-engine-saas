
import os
import logging
import pandas as pd
from src.youtube_client import YouTubeClient
from src.data_processor import DataProcessor
from src.sentiment_engine import SentimentEngine
from src.ai_strategist import AIStrategist
from src.credit_manager import CreditManager
from src.payment_manager import PaymentManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FullSystemTest")

def run_full_test():
    test_user_id = "test_user_debug_999"
    # Trying multiple IDs to ensure we find one that works
    channels_to_try = ["UCX6OQ3DkcsC7P66q3on9L6w", "UC_x5XG1OV2sSZZsBOfS9qCw", "UCs-LH96uS_S36kO9In_6sDw"]

    print("\n--- 🚀 STARTING DEBUGGED INTEGRATION TEST 🚀 ---\n")

    try:
        print("[1/5] Testing Infrastructure Initialization...")
        yt = YouTubeClient()
        proc = DataProcessor()
        sent = SentimentEngine()
        strat = AIStrategist()
        cred = CreditManager()
        pay = PaymentManager()
        print("✅ All components initialized.")

        print("\n[2/5] Testing Credit System...")
        initial = cred.get_user_credits(test_user_id)
        print(f"Balance: {initial} 🪙")
        success, new_bal = cred.deduct_credit(test_user_id)
        if success:
            print(f"✅ Credit deducted. New Balance: {new_bal} 🪙")
        else:
            print("❌ Credit deduction failed.")
            return

        print("\n[3/5] Testing Data Pipeline...")
        videos = None
        for cid in channels_to_try:
            print(f"Attempting to fetch data for channel: {cid}...")
            try:
                videos = yt.get_top_videos(cid, limit=5)
                if videos:
                    print(f"✅ Success with channel {cid}!")
                    break
            except Exception as e:
                print(f"Attempt for {cid} failed: {e}")
        
        if not videos:
            print("❌ All channel fetch attempts failed. Check API Key/Quota.")
            return

        df = pd.DataFrame(videos)
        df = proc.calculate_engagement(df)
        summary = proc.summarize_for_ai(df)
        print(f"✅ Data processed. Summary length: {len(summary)} chars.")

        print("\n[4/5] Testing AI Intelligence Layer...")
        sample_comments = ["Great video!", "I hate this", "Informative!"]
        sentiment = sent.analyze_sentiment(sample_comments, depth="Light", strategy_client=strat)
        if sentiment and 'Positive' in sentiment:
            print(f"✅ Sentiment analysis successful: {sentiment}")
        else:
            print("❌ Sentiment analysis failed.")
            return

        strategy = strat.generate_growth_plan(summary)
        if strategy and len(strategy) > 50:
            print("✅ Growth strategy generated.")
        else:
            print("❌ Strategy generation failed.")
            return

        print("\n[5/5] Testing Payment Integration...")
        url = pay.create_checkout_session(test_user_id, "starter")
        if url and "stripe.com" in url:
            print(f"✅ Stripe URL created: {url[:50]}...")
        else:
            print("❌ Stripe session failed.")
            return

        print("\n--- 🎉 ALL SYSTEMS OPERATIONAL! FULL TEST PASSED 🎉 ---")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_full_test()
