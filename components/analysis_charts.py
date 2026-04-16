import streamlit as st
import plotly.express as px
from streamlit_echarts import st_echarts

def render_viral_pattern_chart(df, x_col, y_col):
    """Renders a scatter plot to find correlations."""
    st.markdown(f"#### {x_col} vs {y_col} Correlation")
    fig = px.scatter(
        df, x=x_col, y=y_col, 
        hover_name="title", 
        template="plotly_dark",
        color=y_col,
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

def render_sentiment_donut(distribution):
    """Renders a donut chart for audience emotion."""
    st.markdown("#### Community Emotion Map")
    
    options = {
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "data": [
                {"value": distribution.get("Positive", 0), "name": "Positive", "itemStyle": {"color": "#00FF00"}},
                {"value": distribution.get("Negative", 0), "name": "Negative", "itemStyle": {"color": "#FF0000"}},
                {"value": distribution.get("Neutral", 0), "name": "Neutral", "itemStyle": {"color": "#CCCCCC"}},
            ],
            "label": {"show": True, "formatter": "{b}: {d}%"}
        }]
    }
    st_echarts(options=options, height="300px")
