print("Script started")
"""
gemini-video-service
Quick CLI entry point: analyse a short video clip with Gemini
"""
from PIL import Image
import sys, json
from pathlib import Path
import cv2
import google.generativeai as genai
from .config import *
from .s3_client import S3Client
import tempfile
import os

def extract_frames(video_path: Path,
    seconds: int = FRAME_WINDOW_SECONDS,
    frames_per_window: int = FRAME_PER_WINDOW):
    print(f"Extracting frames from {video_path}")   # New
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():                          # New
        print("Error: Cannot open video file")      # New
        return []                                   # New
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(seconds * fps)
    step = max(total // frames_per_window, 1)
    frames = []
    for idx in range(0, total, step):
        print(f"Capturing frame {idx}")             # New
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if ok:
            frames.append(frame)
        else:                                       # New
            print("Error: Unable to grab frame")    # New
        if len(frames) >= frames_per_window:
            break
    cap.release()
    print("Finished extracting frames")             # New
        return frames

def analyse_frames(frames):
    print("Analysing frames")                      # New
    genai.configure(api_key=GOOGLE_API_KEY)
    model  = genai.GenerativeModel(GEMINI_MODEL)
    prompt = (
        "You will receive several images extracted from a ~5-second video segment."
        "Analyze them and return a JSON object with the following fields:"
        "{\"captions\", \"brief description\". \"objects\": [\"list\", \"of\", \"objects\"], "
        "\"actions\": [\list\", \"of\", \"actions\"], \"scene\": \"scene description\"}"
    )
    imgs = [Image.fromarray(f) for f in frames]
    for i, img in enumerate(imgs):                  # New
        print(f"Frame {i} prepared for Gemini")     # New
    resp   = model.generate_content([prompt, *imgs])
    print("Received response from Gemini")          # New

    response_text = resp.text.strip()
    print("Gemini Response:", response_text)

    try:
        return response_text if response_text.startswith("{") else "{}"
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    return "{}"

def analyse_video_segment(path: str, save_to_s3: bool = False):
    """
    Analyze video from local path or S3 URI

    Args:
        path: Local file path or s3://bucket/key URI
        save_to_s3: Whether to save caption back to S3
    """
    print(f"Analysing video segment: {path}")

    # Handle S3 URIs
    local_path = path
    s3_key = None
    temp_file = None

    if path.startswith('s3://'):
        print("Detected S3 URI, downloading...")
        s3_client = S3Client()
        s3_key = path.replace(f's3://{os.getenv("S3_BUCKET_NAME")}/', '')
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        local_path = temp_file.name
        s3_client.download_video(s3_key, local_path)
        print(f"Downloaded to {local_path}")

    # Extract and analyze
    frames = extract_frames(Path(local_path))
    if not frames:
        print("Error: No frames extracted")
        return {}

    print("Frames extracted")
    json_text = analyse_frames(frames)
    if not json_text:
        print("Error: No JSON received")
        return {}

    result = json.loads(json_text)

    # Save caption to S3 if requested
    if save_to_s3 and s3_key:
        caption_key = s3_key.replace('videos/', 'captions/').replace('.mp4', '.json')
        s3_client = S3Client()
        s3_uri = s3_client.upload_caption(json_text, caption_key)
        print(f"Caption saved to {s3_uri}")
        result['caption_uri'] = s3_uri

    # Clean up temp file
    if temp_file:
        os.unlink(local_path)
        print("Cleaned up temporary file")

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m src.main <path/to/video.mp4|s3://bucket/key> [--save-to-s3]")
    
    video_path = sys.argv[1]
    save_to_s3 = '--save-to-s3' in sys.argv
    
    print("Processing complete; outputting JSON")
    print(json.dumps(analyse_video_segment(video_path, save_to_s3), indent=2))
