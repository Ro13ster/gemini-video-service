import os
from dotenv import load_dotenv

# Load variables from a lacal .env file
load_dotenv()

# Public configureation values
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FRAME_WINDOW_SECONDS = int(os.getenv("FRAME_WINDOW_SECONDS", "5"))
FRAME_PER_WINDOW = int(os.getenv("FRAME_PER_WINDOW", "5"))