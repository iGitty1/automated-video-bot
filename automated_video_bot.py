import googleapiclient.discovery
import pytube
import moviepy.editor as mp
import requests
import os
import schedule
import time

# YouTube API Configuration
YOUTUBE_API_KEY = "AIzaSyCSk-oI8570OFDQ36oLDUF4JdxhmpZz2TI"

# json2video API Configuration
JSON2VIDEO_API_KEY = "KM1hWyGelC5Pr1BJCOvAfddGQiBrj3N0HYNfEJeL"

# Function to search for viral videos on YouTube
def search_viral_videos(api_key, query, max_results=5):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        order="viewCount",
        videoDuration="long",
        maxResults=max_results
    )
    response = request.execute()
    return response.get("items", [])

# Function to download video from YouTube
def download_video(video_id, output_path="."):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = pytube.YouTube(youtube_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    stream.download(output_path)

# Function to trim video to main action parts
def trim_video(input_path, output_path, start_time, end_time):
    video = mp.VideoFileClip(input_path)
    trimmed_video = video.subclip(start_time, end_time)
    trimmed_video.write_videofile(output_path)

# Function to add ASMR effects using json2video API
def add_asmr_effects(api_key, video_path, output_path):
    url = "https://api.json2video.com/v1/videos"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "input_video_path": video_path,
        "output_video_path": output_path,
        "effects": ["asmr"]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("ASMR effects added successfully.")
    else:
        print("Failed to add ASMR effects:", response.text)

# Function to upload video to YouTube
def upload_video_to_youtube(api_key, video_path, title, description, tags):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # Category ID for People & Blogs
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    media = googleapiclient.http.MediaFileUpload(video_path)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print("Video uploaded successfully:", response["id"])

# Main job function to execute all steps
def job():
    # Step 1: Search for viral videos
    videos = search_viral_videos(YOUTUBE_API_KEY, "viral videos")
    if not videos:
        print("No viral videos found.")
        return
    
    # Step 2: Download the first video
    video_id = videos[0]['id']['videoId']
    download_video(video_id, output_path="downloaded_video.mp4")
    
    # Step 3: Trim the video
    trim_video("downloaded_video.mp4", "trimmed_video.mp4", start_time=30, end_time=60)
    
    # Step 4: Add ASMR effects
    add_asmr_effects(JSON2VIDEO_API_KEY, "trimmed_video.mp4", "asmr_video.mp4")
    
    # Step 5: Upload to YouTube
    upload_video_to_youtube(YOUTUBE_API_KEY, "asmr_video.mp4", "ASMR Viral Video", "Enjoy this ASMR viral video!", ["ASMR", "viral", "shorts"])

# Schedule the job to run every hour
schedule.every().hour.do(job)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
