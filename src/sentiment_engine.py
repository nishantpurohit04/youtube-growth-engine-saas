import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentimentEngine")

class SentimentEngine:
    def __init__(self):
        # Local model removed to ensure Cloud-Native compatibility (no torch/transformers)
        pass

    def analyze_sentiment(self, text_list, depth="Deep", strategy_client=None):
        """
        Analyzes a list of comments and returns a distribution of emotions.
        Delegates all analysis to the AIStrategist to maintain a thin client.
        """
        if not text_list:
            return {"Positive": 0, "Negative": 0, "Neutral": 0}
            
        if not strategy_client:
            logger.error("SentimentEngine: No strategy_client provided. Cannot perform analysis.")
            return {"Positive": 0, "Negative": 0, "Neutral": 0}
            
        try:
            logger.info(f"Performing {depth} sentiment analysis for {len(text_list)} comments.")
            # Delegate to the AI strategist's contextual analysis
            # This handles both 'Light' and 'Deep' requests via the unified Gemini API
            results = strategy_client.analyze_comments_contextually(text_list)
            return results
        except Exception as e:
            logger.error(f"Sentiment Analysis Error: {str(e)}")
            return {"Positive": 0, "Negative": 0, "Neutral": 0}
