import streamlit as st

def render_strategy_panel(strategy_text):
    """Renders the AI-generated strategy output area."""
    st.markdown("### 🤖 AI Strategy Consultant")
    if strategy_text:
        st.markdown(strategy_text)
    else:
        st.info("Enter a Channel ID and run analysis to generate a growth strategy.")
