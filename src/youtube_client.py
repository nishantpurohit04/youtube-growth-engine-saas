import os
import logging
from googleapiclient.discovery import build
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, timedelta, timezone


# Load environment variables
load_dotenv()

logger = logging.getLogger("YouTubeClient")

class YouTubeClient:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables.")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.db = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            if not firebase_admin._apps:
                secret = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not secret:
                    logger.warning("FIREBASE_SERVICE_ACCOUNT_KEY not found. Caching will be unavailable.")
                    return
                
                import json
                cred_path = secret if os.path.exists(secret) else os.path.join(os.getcwd(), secret)
                if secret.strip().startswith('{'):
                    import json
                    cred_dict = json.loads(secret)
                    # Sanitize private key to ensure newlines are handled correctly
                    if 'private_key' in cred_dict:
                        cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
                    cred = credentials.Certificate(cred_dict)
                else:
                    cred = credentials.Certificate(cred_path)
                
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("Firestore initialized for YouTubeClient caching.")
        except Exception as e:
            logger.error(f"Firebase Admin initialization failed for YouTubeClient: {str(e)}")

    def _get_cached_data(self, key):
        """Retrieves data from Firestore if it exists and is less than 24 hours old."""
        if not self.db:
            return None
        
        try:
            doc_ref = self.db.collection("yt_cache").document(key)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                timestamp = data.get("timestamp")
                if timestamp and (datetime.now(timezone.utc) - timestamp).total_seconds() < 86400:
                    return data.get("payload")
        except Exception as e:
            logger.error(f"Firestore cache read error for {key}: {e}")
        
        return None

    def _set_cached_data(self, key, payload):
        """Saves data to Firestore with a timestamp."""
        if not self.db:
            return
        
        try:
            self.db.collection("yt_cache").document(key).set({
                "payload": payload,
                "timestamp": datetime.now(timezone.utc)
            })
        except Exception as e:
            logger.error(f"Firestore cache write error for {key}: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_channel_stats(self, channel_id):
        """Returns basic channel metadata."""
        cache_key = f"stats_{channel_id}"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        request = self.youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        if not response.get("items"):
            return None
            
        data = response["items"][0]
        self._set_cached_data(cache_key, data)
        return data

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_top_videos(self, channel_id, limit=50):
        """
        Returns a list of all-time top videos sorted by view count.
        Implements Firestore caching to avoid quota exhaustion.
        """
        cache_key = f"top_videos_{channel_id}_{limit}"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        videos = []
        next_page_token = None
        
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
                
        video_stats = []
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
                    "duration": item["contentDetails"]["duration"],
                    "tags": item["snippet"].get("tags", []),
                    "description": item["snippet"]["description"]
                })
                
        self._set_cached_data(cache_key, video_stats)
        return video_stats

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_video_comments(self, video_id, max_comments=100):
        """Returns text of comments."""
        # Comments are highly dynamic, we skip caching here to maintain freshness, 
        # but we keep the retry logic for reliability.
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
