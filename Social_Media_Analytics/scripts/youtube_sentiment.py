import os
import googleapiclient.discovery
from dotenv import load_dotenv
from textblob import TextBlob

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("❌ ERROR: API_KEY not found in .env file. Please ensure it is set in the .env file.")

    exit(1)

def get_video_data(video_id):
    """Fetches video details like title, views, likes, and comments count."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    if "items" not in response or len(response["items"]) == 0:
        return None  # Video not found

    video_info = response["items"][0]
    statistics = video_info.get("statistics", {})

    return {
        "title": video_info["snippet"]["title"],
        "views": int(statistics.get("viewCount", 0)),
        "likes": int(statistics.get("likeCount", 0)),
        "comments": int(statistics.get("commentCount", 0))
    }

def get_latest_comments(video_id, max_results=10):
    """Fetches the latest comments from the YouTube video."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()
    except Exception as e:
        print(f"❌ ERROR: Unable to fetch comments - {e}. Please check the video ID and try again.")
        return []


    comments = []
    if "items" in response:
        for item in response["items"]:
            comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment_text)

    return comments

def analyze_sentiment(comments):
    """Performs sentiment analysis on comments and categorizes them."""
    results = []
    for comment in comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0:
            sentiment = "Positive 😊"
        elif polarity < 0:
            sentiment = "Negative 😡"
        else:
            sentiment = "Neutral 😐"

        results.append({"comment": comment, "sentiment": sentiment})

    return results

def print_youtube_analysis(video_id):
    """Fetches video details, latest comments, and prints sentiment analysis in a readable format."""
    video_data = get_video_data(video_id)
    if not video_data:
        print("\n❌ Error: Video not found! Please check the Video ID.")
        return

    # Print Video Details
    print("\n🎬 Video Details:")
    print(f"Title: {video_data['title']}")
    print(f"👁️ Views: {video_data['views']}")
    print(f"👍 Likes: {video_data['likes']}")
    print(f"💬 Total Comments: {video_data['comments']}")

    # Fetch and Print Latest Comments with Sentiment
    comments = get_latest_comments(video_id)
    if not comments:
        print("\n⚠️ No comments found.")
        return
    
    print("\n📝 Latest Comments with Sentiment Analysis:")
    for i, result in enumerate(analyze_sentiment(comments), start=1):
        print(f"\nComment {i}: {result['comment']}")
        print(f"🔹 Sentiment: {result['sentiment']}")

# Run script for testing
if __name__ == "__main__":
    video_id = input("Enter YouTube Video ID: ").strip()
    print_youtube_analysis(video_id)
