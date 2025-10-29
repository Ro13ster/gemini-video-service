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

def analyse_frames(frames):
    print("Analysing frames")                      # New
    genai.configure(api_key=GOOGLE_API_KEY)
    model  = genai.GenerativeModel(GEMINI_MODEL)
    prompt = (
        "You will receive several images extracted from a ~5-second video segment...\n"
        # Continued...
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

def analyse_video_segment(path: str):
    print(f"Analysing video segment: {path}")       # New
    frames = extract_frames(Path(path))
    if not frames:                                  # New
        print("Error: No frames extracted")         # New
        return {}                                   # New
    print("Frames extracted")                       # New
    json_text = analyse_frames(frames)
    if not json_text:                               # New
        print("Error: No JSON received")            # New
        return {}                                   # New
    return json.loads(json_text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m src.main path/to/video.mp4")
        
    print("Processing complete; outputting JSON")
    print(json.dumps(analyse_video_segment(sys.argv[1]), indent=2))
