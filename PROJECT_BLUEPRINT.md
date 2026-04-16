# 🚀 PROJECT BLUEPRINT: YouTube Content Growth Engine (SaaS Version)

## 📌 Overview
An AI-powered analytics suite for YouTube creators that provides prescriptive growth strategies by analyzing channel performance and audience sentiment.

### Core Value Proposition
Moving from "Descriptive Analytics" (what happened) to "Prescriptive Strategy" (what to do next).

---

## 🛠️ Technical Specifications

### Model & AI
- **LLM Model:** `gemma-4-31b-it` (Crucial: must use this exact model).
- **AI Engine:** Google Gemini API via `google-generativeai` library.
- **Resilience:** Implement exponential backoff retry logic for API calls to handle `429 Too Many Requests` errors.
- **Sentiment Logic:**
    - **Unified API Analysis:** Use `gemma-4-31b-it` for both light and deep sentiment analysis to eliminate heavy local dependencies (torch/transformers) and prevent OOM crashes on free hosting.
    - **Reasoning:** Distinguish between \"Technical Frustration\" (Neutral/Positive) and \"Content Hate\" (Negative).

### Data Engineering
- **API:** YouTube Data API v3.
- **Fetch Strategy:** Use `search().list(order='viewCount')` to get all-time top videos, NOT the uploads playlist (which is chronological).
- **Caching Strategy:** Store YouTube API results in Firestore with a 24-hour TTL (Time-to-Live) to minimize API quota consumption.
- **Duration Parsing:** Use the custom `parse_iso_duration` function to convert ISO 8601 (`PT...`) to decimal minutes.
- **Metrics:** Engagement Rate = `((likes + comments) / views) * 100`.

### Frontend & UX
- **Framework:** Streamlit.
- **Style:** Dark mode, Glassmorphism via `assets/style.css`.
- **Key Visuals:** 
    - KPI Cards (Total Reach, Avg Engagement, Sentiment Index, Viral Score).
    - Scatter Plot: `duration_min` vs `view_count`.
    - Donut Chart: Sentiment Distribution.

---

## 💰 SaaS Business Logic (The "Zero-Dollar" Plan)

### Hosting Strategy
- **Platform:** Streamlit Community Cloud or Hugging Face Spaces (Free Tiers).
- **Weight:** Must remain "Cloud-Native." Remove heavy libraries (`torch`, `transformers`) to avoid OOM crashes on free hosting.

### Monetization Model
- **SaaS Architecture:** User-based access.
- **Authentication:** Google Firebase Auth.
- **Database:** Firebase Firestore (storing user profiles and credit balances).
- **Payment:** Stripe (Pay-as-you-earn, no upfront cost).
- **Credit System:** 
    - User signs up $\rightarrow$ gets X free credits.
    - 1 Analysis = 1 Credit.
    - Buy more credits via Stripe.

---

## 🗺️ Execution Roadmap

### Phase 1: Infrastructure & Cleanup
- Transition to a thin, API-only client (remove `torch`/`transformers`).
- Setup secure Secret Management for Cloud deployment.

### Phase 2: Identity & Access
- Integrate Firebase Auth (Login/Signup).
- Implement session-based access control.

### Phase 3: The Economic Engine
- Create Firestore database for credit tracking.
- Implement credit deduction logic on "Refresh Data."

### Phase 4: Payments
- Integrate Stripe Checkout for credit purchases.
- Implement automatic credit fulfillment via Webhooks.

### Phase 5: Launch
- Deploy to Cloud $\rightarrow$ Beta Test $\rightarrow$ Polish UX.

---

## 📝 Session Hand-off Note
When restarting a session, the AI agent MUST read this file first to regain all project context, constraints, and logic.
