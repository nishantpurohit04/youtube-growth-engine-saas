import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIStrategist:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            pass
        else:
            genai.configure(api_key=self.api_key)
            # Locked to the exact model requested: gemma-4-31b-it
            self.model = genai.GenerativeModel('gemma-4-31b-it')

    def generate_growth_plan(self, data_summary):
        """
        Constructs the prompt and calls the model for growth tips.
        """
        if not self.api_key:
            return "⚠️ Gemini API Key not configured. Please add GEMINI_API_KEY to .env"

        prompt = (
            f"You are a world-class YouTube Strategist. I will provide you with a dataset of a channel's top videos. \n\n"
            f"DATA SUMMARY:\n{data_summary}\n\n"
            f"Based on the correlation between video length, titles, and engagement, identify the 3 most successful patterns. "
            f"Then, suggest 3 specific video ideas that leverage these patterns to increase views by 20%."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating strategy: {str(e)}"

    def analyze_comments_contextually(self, text_list):
        """
        Universal nuanced sentiment analysis.
        Distinguishes between frustration with the subject vs frustration with the creator.
        """
        if not self.api_key:
            return {"Positive": 0, "Negative": 0, "Neutral": 0}

        # Join comments into a numbered list
        comments_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(text_list)])
        
        prompt = (
            f"You are an expert audience analyst for YouTube. Analyze the following comments for a channel.\n\n"
            f"CRITICAL LOGIC: Distinguish between 'External Frustration' and 'Internal Frustration'.\n"
            f"- External Frustration: Users complaining about the topic, their tools, the situation, or the problem they are facing. This is NEUTRAL or POSITIVE for the creator because the user is engaging with the topic.\n"
            f"- Internal Frustration: Users hating the video quality, the creator's delivery, or the actual instructions. This is NEGATIVE.\n\n"
            f"COMMENTS:\n{comments_text}\n\n"
            f"Return ONLY a JSON object with the keys 'Positive', 'Negative', and 'Neutral' containing the percentage of comments for each. "
            f"Example: {{\"Positive\": 60, \"Negative\": 10, \"Neutral\": 30}}"
        )

        try:
            # Using JSON mode for reliable parsing
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Contextual Analysis Error: {e}")
            return {"Positive": 0, "Negative": 0, "Neutral": 0}
