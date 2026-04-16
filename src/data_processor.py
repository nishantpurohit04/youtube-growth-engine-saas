import pandas as pd
import numpy as np
import re

class DataProcessor:
    @staticmethod
    def parse_iso_duration(duration_str):
        """
        Converts ISO 8601 duration (e.g., PT1H2M30S) to total minutes as a float.
        """
        if not duration_str or not isinstance(duration_str, str):
            return 0.0
            
        # Regex to find hours, minutes, and seconds
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)
        
        total_minutes = 0.0
        if hours:
            total_minutes += int(hours.group(1)) * 60
        if minutes:
            total_minutes += int(minutes.group(1))
        if seconds:
            total_minutes += int(seconds.group(1)) / 60.0
            
        return total_minutes

    @staticmethod
    def calculate_engagement(df):
        """
        Adds 'engagement_rate' column to the dataframe.
        Formula: (likes + comments) / views * 100
        """
        if df.empty:
            return df
            
        df['engagement_rate'] = (
            (df['like_count'] + df['comment_count']) / 
            df['view_count'].replace(0, 1) # Avoid division by zero
        ) * 100
        
        return df

    @staticmethod
    def get_correlations(df, x_col, y_col):
        """
        Returns correlation coefficient between two columns.
        """
        if df.empty or x_col not in df.columns or y_col not in df.columns:
            return 0.0
            
        return df[x_col].corr(df[y_col])

    @staticmethod
    def summarize_for_ai(df):
        """
        Converts the DataFrame into a text summary for Gemini.
        """
        if df.empty:
            return "No data available for analysis."
            
        total_views = df['view_count'].sum()
        avg_engagement = df['engagement_rate'].mean()
        
        # Find top 3 videos by views
        top_videos = df.nlargest(3, 'view_count')[['title', 'view_count', 'engagement_rate']]
        top_videos_str = "\n".join([
            f"- {row['title']}: {row['view_count']} views, {row['engagement_rate']:.2f}% eng" 
            for _, row in top_videos.iterrows()
        ])
        
        summary = (
            f"Channel Performance Summary:\n"
            f"- Total Views of Top Videos: {total_views:,}\n"
            f"- Average Engagement Rate: {avg_engagement:.2f}%\n\n"
            f"Top Performing Videos:\n{top_videos_str}\n"
        )
        
        return summary
