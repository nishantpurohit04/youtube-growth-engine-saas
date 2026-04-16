import streamlit as st
import pandas as pd
from src.youtube_client import YouTubeClient
from src.data_processor import DataProcessor
from src.sentiment_engine import SentimentEngine
from src.ai_strategist import AIStrategist
from src.credit_manager import CreditManager
from src.payment_manager import PaymentManager, CREDIT_PACKAGES
from components.auth import render_auth_screen, sign_out
from components.kpi_cards import render_kpi_card
from components.analysis_charts import render_viral_pattern_chart, render_sentiment_donut
from components.strategy_panel import render_strategy_panel

# Page Config
st.set_page_config(
    page_title="YouTube Content Growth Engine",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for Premium Look
with open("assets/style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "data" not in st.session_state:
    st.session_state.data = None
if "sentiment" not in st.session_state:
    st.session_state.sentiment = None
if "strategy" not in st.session_state:
    st.session_state.strategy = None

# --- AUTH GUARD ---
if st.session_state.user is None:
    render_auth_screen()
    st.stop() # Stop execution here until user is logged in

# Initialize Clients
yt_client = YouTubeClient()
processor = DataProcessor()
sentiment_engine = SentimentEngine()
ai_strategist = AIStrategist()
credit_manager = CreditManager()
payment_manager = PaymentManager()

# --- SIDEBAR ---
with st.sidebar:
    st.title(\"⚙️ Controls\")
    
    # User Profile & Logout
    user = st.session_state.user
    user_email = user.get('email', 'User')
    user_id = user.get('localId') # Firebase UID
    
    st.markdown(f\"**Logged in as:** {user_email}\")
    
    # Credit Balance Display
    credits = credit_manager.get_user_credits(user_id)
    if credits is not None:
        st.metric(\"Credits Remaining\", f\"{credits} 🪙\")
    else:
        st.warning(\"Unable to load credits.\")
        
    # --- CREDIT SHOP ---
    with st.expander(\"💳 Buy More Credits\"):
        st.write(\"Choose a package to upgrade your account:\")
        for pkg_id, (price, count) in CREDIT_PACKAGES.items():
            if st.button(f\"{pkg_id.capitalize()} Pack: {count} credits for ₹{price}\", key=f\"pkg_{pkg_id}\", use_container_width=True):
                with st.spinner(\"Creating secure payment session...\"):
                    url = payment_manager.create_checkout_session(user_id, pkg_id)
                    if url:
                        st.markdown(f\"<a href='{url}' target='_blank' style='text-decoration:none;'>🚀 Click here to pay with Stripe</a>\", unsafe_allow_html=True)
                        st.info(\"Opening payment page in a new tab...\")
                    else:
                        st.error(\"Could not create payment session. Please try again.\")

    if st.button(\"Logout\", use_container_width=True):
        sign_out()
        st.rerun()
    
    st.markdown(\"--- \")
    channel_id = st.text_input(\"Enter Channel ID\", placeholder=\"UC...\")



    date_range = st.date_input("Date Range")
    analysis_depth = st.select_slider("Analysis Depth", options=["Light", "Deep"], value="Light")
    
    if st.button(\"🔄 Refresh Data\", use_container_width=True):
        if channel_id:
            # --- CREDIT CHECK ---
            user_id = st.session_state.user.get('localId')
            current_credits = credit_manager.get_user_credits(user_id)
            
            if current_credits is None or current_credits < 1:
                st.error(\"❌ Insufficient credits! Please purchase more to run analysis.\")
                st.stop()
            
            with st.spinner(f\"Running {analysis_depth} analysis...\"):
                try:
                    fetch_limit = 100 if analysis_depth == \"Deep\" else 50
                    raw_videos = yt_client.get_top_videos(channel_id, limit=fetch_limit)
                    df = pd.DataFrame(raw_videos)
                    df = processor.calculate_engagement(df)
                    st.session_state.data = df
                    
                    top_5_ids = df.nlargest(5, 'view_count')['video_id'].tolist()
                    all_comments = []
                    for vid in top_5_ids:
                        all_comments.extend(yt_client.get_video_comments(vid, max_comments=20))
                    
                    st.session_state.sentiment = sentiment_engine.analyze_sentiment(
                        all_comments, 
                        depth=analysis_depth, 
                        strategy_client=ai_strategist
                    )
                    
                    summary = processor.summarize_for_ai(df)
                    st.session_state.strategy = ai_strategist.generate_growth_plan(summary)
                    
                    # --- CREDIT DEDUCTION ---
                    credit_manager.deduct_credit(user_id)
                    
                    st.success(f\"{analysis_depth} Analysis Complete! 1 credit deducted.\")
                except Exception as e:
                    st.error(f\"Error: {e}\")
        else:
            st.warning(\"Please enter a Channel ID.\")

    st.markdown("---")
    if st.button("📥 Export Report", use_container_width=True):
        if st.session_state.data is not None:
            df_export = st.session_state.data.copy()
            df_export['duration_min'] = df_export['duration'].apply(processor.parse_iso_duration)
            csv = df_export.to_csv(index=False)
            st.download_button("Download CSV", csv, "youtube_report.csv", "text/csv")

# --- MAIN CONTENT ---
st.markdown("<h1 style='text-align: center;'>📈 Content Growth Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Transform raw metrics into actionable growth strategies</p>", unsafe_allow_html=True)

if st.session_state.data is not None:
    df = st.session_state.data.copy()
    df['duration_min'] = df['duration'].apply(processor.parse_iso_duration)
    
    # KPI ROW
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Reach", f"{df['view_count'].sum():,}", icon="👁️")
    with col2:
        render_kpi_card("Avg Engagement", f"{df['engagement_rate'].mean():.2f}%", icon="🔥")
    with col3:
        # SAFETY: Added (st.session_state.sentiment or {}) to prevent NoneType error
        sentiment_val = (st.session_state.sentiment or {}).get('Positive', 0)
        render_kpi_card("Sentiment Index", f"{sentiment_val:.1f}%", icon="😊")
    with col4:
        viral_score = (df['view_count'].max() / df['view_count'].mean()) * 10 if not df.empty else 0
        render_kpi_card("Viral Score", f"{viral_score:.1f}", icon="🚀")

    st.markdown("---")

    # ANALYTICS SECTION
    row2_col1, row2_col2 = st.columns([2, 1])
    with row2_col1:
        render_viral_pattern_chart(df, "duration_min", "view_count")

    with row2_col2:
        # SAFETY: Added default empty dict for the donut chart
        render_sentiment_donut(st.session_state.sentiment or {})

    st.markdown("---")

    # TOP CONTENT TABLE
    st.markdown("#### 🏆 Top Performing Content")
    display_cols = ['title', 'view_count', 'engagement_rate', 'duration_min']
    st.table(df.nlargest(10, 'view_count')[display_cols])

    st.markdown("---")

    # AI STRATEGY
    render_strategy_panel(st.session_state.strategy)

else:
    st.info("👈 Enter a YouTube Channel ID in the sidebar to start your analysis.")
