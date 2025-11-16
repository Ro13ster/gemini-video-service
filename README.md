# Gemini Video Service

> Serverless video captioning pipeline powered by Google Gemini AI, Ray Serve, and S3 storage

[![CI/CD](https://github.com/Ro13ster/gemini-video-service/actions/workflows/deploy.yml/badge.svg)](https://github.com/Ro13ster/gemini-video-service/actions)

## 🎯 What It Does

Upload a video → Get AI-generated captions with detailed analysis:
- **Caption**: Natural language description
- **Objects**: Detected items in the scene
- **Actions**: What's happening in the video
- **Scene**: Overall context and setting

## 🏗️ Architecture

Serverless video captioning system using Ray Serve API, Google Gemini AI, and S3 storage.

**Key Features:**
- 🚀 **Serverless**: Spins down to 0 instances when idle (pay $0)
- 📈 **Auto-scaling**: Handles 1 to 1000 concurrent users automatically
- ☁️ **Cloud-native**: Deploys to Google Cloud Run in minutes
- 🐳 **Containerized**: Consistent environment everywhere
- 🔄 **CI/CD**: Auto-deploy on git push

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key
- AWS account (for S3 storage)
- Docker (optional)

### Local Setup

**1. Clone and setup:**

```bash
git clone https://github.com/Ro13ster/gemini-video-service.git
cd gemini-video-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment:**

```bash
copy .env.example .env
# Edit .env with your API keys
```

**3. Run:**

```bash
python -m src.main sample.mp4
```

## 🌐 API Usage

**Start the API:**

```bash
serve run src.api:deployment
```

**Upload video:**

```bash
curl -X POST http://localhost:8000/caption/upload -F "file=@video.mp4"
```

## ☁️ Deployment

Push to main branch → GitHub Actions automatically deploys to Cloud Run

## 📁 Project Structure

gemini-video-service/
├── .github/workflows/ # CI/CD
├── src/ # Source code
├── deploy/ # Deployment configs
└── tests/ # Tests

## 💰 Cost

- **Idle**: $0/month (spins down to 0)
- **Active**: ~$0.72/month for 1000 requests/day

## 📝 License

MIT License

---

Built with ❤️ using Google Gemini AI, Ray Serve, and FastAPI