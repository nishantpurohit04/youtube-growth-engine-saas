import streamlit as st

def render_strategy_panel(strategy_text):
    """Renders the AI-generated strategy output area."""
    st.markdown("### 🤖 AI Strategy Consultant")
    if strategy_text:
        st.markdown(
            f"""
            <div style="background-color: rgba(0, 209, 255, 0.1); 
                        border-left: 5px solid #00D1FF; 
                        padding: 20px; 
                        border-radius: 10px; 
                        color: white; 
                        font-style: italic;">
                {strategy_text}
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.info("Enter a Channel ID and run analysis to generate a growth strategy.")
