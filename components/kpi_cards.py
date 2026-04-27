import streamlit as st

def render_kpi_card(label, value, delta=None, icon="📈"):
    """Renders a premium KPI card with a delta indicator using custom HTML for perfect alignment."""
    delta_html = ""
    if delta is not None:
        color = "#00FF00" if delta > 0 else "#FF0000"
        delta_html = f"<div style='color: {color}; font-weight: bold; font-size: 14px;'>{delta:+.2f}%</div>"

    # Use a single string without any newlines or spaces to force raw HTML rendering
    html_content = f'<div class="kpi-card"><div class="kpi-content"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{delta_html}</div><div class="kpi-icon">{icon}</div></div>'
    
    st.markdown(html_content, unsafe_allow_html=True)
