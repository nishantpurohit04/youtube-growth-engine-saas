import streamlit as st
from dotenv import load_dotenv
load_dotenv()
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
    st.stop()

# Initialize Clients
yt_client = YouTubeClient()
processor = DataProcessor()
sentiment_engine = SentimentEngine()
ai_strategist = AIStrategist()
credit_manager = CreditManager()
payment_manager = PaymentManager()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Controls")
    user = st.session_state.user
    user_email = user.get('email', 'User')
    user_id = user.get('localId')
    
    st.markdown(f"**Logged in as:** {user_email}")
    
    credits = credit_manager.get_user_credits(user_id)
    if credits is not None:
        st.metric("Credits Remaining", f"{credits} 🪙")
    else:
        st.warning("Unable to load credits.")
        
    with st.expander("💳 Buy More Credits"):
        st.write("Choose a package to upgrade your account:")
        for pkg_id, (price, count) in CREDIT_PACKAGES.items():
            if st.button(f"{pkg_id.capitalize()} Pack: {count} credits for ${price}", key=f"pkg_{pkg_id}", use_container_width=True):
                with st.spinner("Creating secure payment session..."):
                    url = payment_manager.create_checkout_session(user_id, pkg_id)
                    if url:
                        st.markdown(f"<a href='{url}' target='_blank' style='text-decoration:none;'>🚀 Click here to pay with Stripe</a>", unsafe_allow_html=True)
                        st.info("Opening payment page in a new tab...")
                    else:
                        st.error("Could not create payment session. Please try again.")
    
    if st.button("Logout", use_container_width=True):
        sign_out()
        st.rerun()
    
    st.markdown("--- ")
    channel_id = st.text_input("Enter Channel ID", placeholder="UC...")
    analysis_depth = st.select_slider("Analysis Depth", options=["Light", "Deep"], value="Light")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        if channel_id:
            user_id = st.session_state.user.get('localId')
            current_credits = credit_manager.get_user_credits(user_id)
            
            if current_credits is None or current_credits < 1:
                st.error("❌ Insufficient credits! Please purchase more to run analysis.")
                st.stop()
            
            with st.spinner(f"Running {analysis_depth} analysis..."):
                try:
                    fetch_limit = 100 if analysis_depth == "Deep" else 50
                    raw_videos = yt_client.get_top_videos(channel_id, limit=fetch_limit)
                    df = pd.DataFrame(raw_videos)
                    if df.empty:
                        st.error("No videos found for this channel. Please check the Channel ID.")
                        st.stop()
                    df = processor.calculate_engagement(df)
                    st.session_state.data = df
                    
                    summary = processor.summarize_for_ai(df)
                    st.session_state.strategy = ai_strategist.generate_growth_plan(summary)
                    
                    success, new_balance = credit_manager.deduct_credit(user_id)
                    if success:
                        st.toast(f"{analysis_depth} Analysis Complete! 1 credit deducted. Remaining: {new_balance} 🪙", icon="✅")
                    else:
                        st.error("Credit deduction failed. Please check your balance.")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a Channel ID.")
    st.markdown("---")
    if st.button("📥 Export Report", use_container_width=True):
        if st.session_state.data is not None:
            df_export = st.session_state.data.copy()
            df_export['duration_min'] = df_export['duration'].apply(processor.parse_iso_duration)
            csv = df_export.to_csv(index=False)
            filename = f"growth_report_{channel_id}.txt"
            report_text = f"YouTube Growth Report\n{'='*20}\n\nAI Strategy:\n{st.session_state.strategy}\n\n{'='*20}\nData:\n{csv}"
            st.download_button("Download Full Report (TXT)", report_text, filename, "text/plain")
            st.download_button("Download Data Only (CSV)", csv, "youtube_data.csv", "text/csv")

# --- MAIN CONTENT ---
st.markdown("<h1 style='text-align: center;'>📈 Content Growth Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Transform raw metrics into actionable growth strategies</p>", unsafe_allow_html=True)

if st.session_state.data is not None and not st.session_state.data.empty:
    df = st.session_state.data.copy()
    df['duration_min'] = df['duration'].apply(processor.parse_iso_duration)
    
    # KPI ROW
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        render_kpi_card("Total Reach", f"{df['view_count'].sum():,}", icon="👁️")
    with col2:
        render_kpi_card("Avg Engagement", f"{df['engagement_rate'].mean():.2f}%", icon="🔥")
    with col3:
        mean_views = df['view_count'].mean()
        viral_score = (df['view_count'].max() / mean_views) * 10 if mean_views > 0 else 0
        render_kpi_card("Viral Score", f"{viral_score:.1f}", icon="🔥")
    
    st.markdown("---")
    
    # ANALYTICS SECTION
    st.markdown("#### 📈 Viral Pattern Analysis")
    st.markdown("Analyzing the correlation between video duration and reach.")
    render_viral_pattern_chart(df, "duration_min", "view_count")
    
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
