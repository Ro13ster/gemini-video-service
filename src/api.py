"""
Ray Serve API wrapper for video captioning service
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from ray import serve
import tempfile
import os
from pathlib import Path
from .main import analyse_video_segment
from .s3_client import S3Client
import uuid

app = FastAPI(title="Video Captioning API")

@serve.deployment(num_replicas=1)
@serve.ingress(app)
class VideoCaptioningService:
    
    @app.post("/caption/upload")
    async def caption_upload(self, file: UploadFile = File(...), save_to_s3: bool = Form(False)):
        """
        Upload a video file and get caption
        
        Args:
            file: Video file to analyze
            save_to_s3: Whether to save video and caption to S3
        """
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            if save_to_s3:
                # Upload to S3 first
                s3_client = S3Client()
                video_key = f"videos/{uuid.uuid4()}.mp4"
                s3_uri = s3_client.upload_video(tmp_path, video_key)
                
                # Process from S3
                result = analyse_video_segment(s3_uri, save_to_s3=True)
            else:
                # Process locally
                result = analyse_video_segment(tmp_path, save_to_s3=False)
            
            return JSONResponse(content=result)
        
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
    
    @app.post("/caption/s3")
    async def caption_s3(self, s3_uri: str = Form(...), save_caption: bool = Form(True)):
        """
        Process video from S3 URI
        
        Args:
            s3_uri: S3 URI (s3://bucket/key)
            save_caption: Whether to save caption back to S3
        """
        try:
            result = analyse_video_segment(s3_uri, save_to_s3=save_caption)
            return JSONResponse(content=result)
        except Exception as e:
            return JSONResponse(
                content={"error": str(e)},
                status_code=500
            )
    
    @app.get("/health")
    async def health(self):
        """Health check endpoint"""
        return {"status": "healthy", "service": "video-captioning"}


# Deployment configuration
deployment = VideoCaptioningService.bind()