import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeClient:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables.")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_channel_stats(self, channel_id):
        """Returns basic channel metadata."""
        request = self.youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get("items"):
            return None
            
        return response["items"][0]

    def get_top_videos(self, channel_id, limit=50):
        """
        Returns a list of all-time top videos sorted by view count.
        Uses search().list with order='viewCount' instead of the uploads playlist.
        """
        videos = []
        next_page_token = None
        
        # Use search.list to get videos sorted by viewCount
        while len(videos) < limit:
            search_request = self.youtube.search().list(
                part="id",
                channelId=channel_id,
                order="viewCount",
                type="video",
                maxResults=min(50, limit - len(videos)),
                pageToken=next_page_token
            )
            search_response = search_request.execute()
            
            for item in search_response.get("items", []):
                videos.append(item["id"]["videoId"])
                
            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break
                
        # Now get detailed statistics for these specific video IDs
        video_stats = []
        # API allows requesting stats for up to 50 videos at a time
        for i in range(0, len(videos), 50):
            batch = videos[i:i+50]
            stats_request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch)
            )
            stats_response = stats_request.execute()
            
            for item in stats_response.get("items", []):
                video_stats.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                    "duration": item["contentDetails"]["duration"], # ISO 8601 format
                    "tags": item["snippet"].get("tags", []),
                    "description": item["snippet"]["description"]
                })
                
        return video_stats

    def get_video_comments(self, video_id, max_comments=100):
        """Returns text of comments."""
        comments = []
        next_page_token = None
        
        while len(comments) < max_comments:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
                
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
                
        return comments
