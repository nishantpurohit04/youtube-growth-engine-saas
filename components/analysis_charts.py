import streamlit as st
import plotly.express as px
import numpy as np
from streamlit_echarts import st_echarts

def render_viral_pattern_chart(df, x_col, y_col):
    """
    Renders a scatter plot showing the correlation between video length and view count.
    Includes normalized bubble sizing to prevent visual imbalance.
    """
    df = df.copy()
    max_val = df[y_col].max()
    min_val = df[y_col].min()
    
    if max_val != min_val:
        df["bubble_size"] = 10 + ((df[y_col] - min_val) / (max_val - min_val)) * 50
    else:
        df["bubble_size"] = 20

    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col, 
        color="engagement_rate",
        size="bubble_size",
        hover_data=["title"],
        labels={x_col: "Duration (Min)", y_col: "Views"},
        template="plotly_dark",
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zeroline=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_sentiment_donut(sentiment_data):
    """
    Renders a donut chart showing the distribution of audience sentiment.
    """
    st.markdown("#### 😊 Audience Sentiment")
    
    if not sentiment_data or sum(sentiment_data.values()) == 0:
        st.info("No sentiment data available for the top videos.")
        return

    options = {
        "tooltip": {"trigger": "item"},
        "legend": {
            "top": "bottom",
            "textStyle": {"color": "white"}
        },
        "series": [
            {
                "name": "Sentiment",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2,
                },
                "label": {
                    "show": False,
                    "position": "center"
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": "20",
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {
                    "show": False
                },
                "data": [
                    {"value": sentiment_data.get("Positive", 0), "name": "Positive", "itemStyle": {"color": "#2ecc71"}},
                    {"value": sentiment_data.get("Negative", 0), "name": "Negative", "itemStyle": {"color": "#e74c3c"}},
                    {"value": sentiment_data.get("Neutral", 0), "name": "Neutral", "itemStyle": {"color": "#f1c40f"}},
                ],
            }
        ],
        "backgroundColor": "transparent"
    }
    
    st_echarts(options=options, height="400px")
