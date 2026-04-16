import streamlit as st

def render_kpi_card(label, value, delta=None, icon="📈"):
    """Renders a premium KPI card with a delta indicator."""
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{label}**")
            st.markdown(f"### {value}")
        with col2:
            st.markdown(f"<div style='text-align: right; font-size: 24px;'>{icon}</div>", unsafe_allow_html=True)
            if delta is not None:
                color = "green" if delta > 0 else "red"
                st.markdown(f"<div style='text-align: right; color: {color}; font-weight: bold;'>{delta:+.2f}%</div>", unsafe_allow_html=True)
