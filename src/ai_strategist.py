import os
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_growth_plan(self, data_summary):
        """
        Constructs the prompt and calls the model for growth tips.
        """
        if not self.api_key:
            return "⚠️ Gemini API Key not configured. Please add GEMINI_API_KEY to .env"

        prompt = (
            f"You are a world-class YouTube Strategist. I will provide you with a dataset of a channel's top videos.\n\n"
            f"DATA SUMMARY:\n{data_summary}\n\n"
            f"TASK: Create a high-end, professional Growth Strategy Report.\n\n"
            f"CRITICAL OUTPUT CONSTRAINT:\n"
            f"Do NOT include your internal reasoning, thinking process, drafting notes, or 'self-correction' in the response. "
            f"Do NOT show the 'goals' or 'tasks' I gave you. "
            f"Output ONLY the final professional report. Start immediately with the first header.\n\n"
            f"FORMATTING RULES:\n"
            f"1. NO robotic labels like '*Length:*' or '*Topics:*'. Use natural language or professional headers.\n"
            f"2. NO LaTeX symbols or technical arrows (e.g., avoid $\\rightarrow$). Use clean, professional language.\n"
            f"3. Use clear Markdown headers (###) to separate the report into sections: '📊 Executive Analysis', '🎯 The Success Patterns', and '🚀 High-Growth Video Ideas'.\n"
            f"4. For the video ideas, provide a clear 'Proposed Title' (incorporating emojis and high-emotion hooks) and a 'Strategic Reason' why it will work.\n"
            f"5. Avoid long, monotonous bullet lists; use a mix of paragraphs and structured points.\n\n"
            f"Based on the correlation between video length, titles, and engagement, identify the 3 most successful patterns. "
            f"Then, suggest 3 specific video ideas that leverage these patterns to increase views by 20%."
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            # --- FAIL-SAFE PROFESSIONAL FILTER ---
            # Look for the start of the actual report regardless of whether the AI used ### or not.
            marker = "📊 Executive Analysis"
            if marker in text:
                # Slice from the marker onwards
                text = text[text.find(marker):]
            
            # Final sanity check: remove any leading "AI Strategy Consultant" artifacts
            if text.startswith("🤖 AI Strategy Consultant"):
                # Find the first actual header if it exists
                if "📊 Executive Analysis" in text:
                    text = text[text.find("📊 Executive Analysis"):]
            
            return text
        except Exception as e:
            # We raise the exception so tenacity can catch it and retry
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_comments_contextually(self, text_list, depth="Light"):
        """
        Universal nuanced sentiment analysis.
        Distinguishes between frustration with the subject vs frustration with the creator.
        """
        if not self.api_key:
            return {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        # Join comments into a numbered list
        comments_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(text_list)])
        
        prompt = (
            f"You are an expert audience analyst for YouTube. Perform a {depth} sentiment analysis on the following comments for a channel.\n\n"
            f"CRITICAL LOGIC: Distinguish between 'External Frustration' and 'Internal Frustration'.\n"
            f"- External Frustration: Users complaining about the topic, their tools, the situation, or the problem they are facing. This is NEUTRAL or POSITIVE for the creator because the user is engaging with the topic.\n"
            f"- Internal Frustration: Users hating the video quality, the creator's delivery, or the actual instructions. This is NEGATIVE.\n\n"
            f"COMMENTS:\n{comments_text}\n\n"
            f"Return ONLY a JSON object with the keys 'Positive', 'Negative', 'Neutral' containing the percentage of comments for each. "
            f"IMPORTANT: The sum of percentages must equal 100. Do not return 0 for all values if comments are present. If you are unsure, categorize as Neutral.\n"
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
            raise e
