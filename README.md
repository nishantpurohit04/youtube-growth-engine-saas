# 📈 YouTube Growth Engine (SaaS)

An AI-powered prescriptive analytics suite for YouTube creators that transforms raw channel metrics into actionable, high-growth strategies.

## 🚀 Overview
Most YouTube analytics tools are **descriptive** (they tell you *what* happened). This engine is **prescriptive** (it tells you *what to do next*). By analyzing top-performing content and audience sentiment, the system identifies growth patterns and suggests specific video ideas to increase reach and engagement.

## 🛠️ Technical Stack
- **AI Engine:** Google Gemini (`gemma-4-31b-it`) for high-reasoning growth strategy and nuanced sentiment analysis.
- **Backend/Auth:** Firebase Auth & Firestore for secure user management and credit-based SaaS billing.
- **Payments:** Stripe API integration for a "pay-as-you-earn" credit system.
- **Frontend:** Streamlit with custom Glassmorphism CSS for a premium, professional UX.
- **Data Source:** YouTube Data API v3 with a custom Firestore caching layer to optimize quota usage.

## ✨ Key Features
- **Prescriptive Strategy:** Generates professional growth reports including Executive Analysis, Success Patterns, and High-Growth Video Ideas.
- **Nuanced Sentiment Analysis:** Distinguishes between "External Frustration" (topic-based) and "Internal Frustration" (creator-based) to provide accurate audience insights.
- **SaaS Economic Engine:** Fully integrated credit system where users purchase analysis credits via Stripe.
- **Viral Pattern Detection:** Analyzes the correlation between video duration and view counts to identify "sweet spots" for content length.
- **Automated Fulfillment:** Stripe Webhooks automatically credit user accounts upon successful payment.

## ⚙️ Installation & Setup
1. **Clone the repo:**
   ```bash
   git clone https://github.com/nishantpurohit04/youtube-growth-engine-saas.git
   cd youtube-growth-engine-saas
   ```

2. **Setup Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   YOUTUBE_API_KEY=your_youtube_key
   GEMINI_API_KEY=your_gemini_key
   STRIPE_SECRET_KEY=your_stripe_key
   FIREBASE_API_KEY=...
   FIREBASE_AUTH_DOMAIN=...
   FIREBASE_PROJECT_ID=...
   FIREBASE_STORAGE_BUCKET=...
   FIREBASE_MESSAGING_SENDER_ID=...
   FIREBASE_APP_ID=...
   FIREBASE_DATABASE_URL=...
   FIREBASE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
   ```

4. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 📈 Growth Roadmap
- [ ] **Architecture Migration:** Moving from Streamlit to a decoupled React + FastAPI stack for sub-second latency and HMR.
- [ ] **Advanced Analytics:** Implementing deeper competitor benchmarking.
- [ ] **Automated Alerts:** Notifying creators when a new "viral trend" matches their channel's success patterns.
