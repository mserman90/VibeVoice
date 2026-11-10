"""
VibeVoice & Türkçe Çok Konuşmacılı Podcast API Sunucusu (FastAPI + PyTorch / CUDA)
Bu sunucu, web stüdyosundan gelen gerçek üretim isteklerini karşılar,
GPU üzerinde VibeVoice ve Türkçe ses sentezleme çıkarımı yapar ve ses akışını (WAV/MP3) döner.
"""

import os
import io
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

app = FastAPI(
    title="PodcastLab GPU Podcast API",
    description="PodcastLab ve VibeVoice Türkçe çok konuşmacılı ses sentezi API'si",
    version="1.3.0"
)

# CORS: GitHub Pages ve tüm web istemcilerinden gelen isteklere izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Türkçe Neural Sesler
TURKISH_VOICES = {
    "Mert": "tr-TR-AhmetNeural",
    "Selin": "tr-TR-EmelNeural",
    "Can": "tr-TR-AhmetNeural",
    "Deniz": "tr-TR-EmelNeural"
}

class SpeakerConfig(BaseModel):
    id: Optional[str] = "spk"
    name: str
    voice: Optional[str] = "default"
    gender: Optional[str] = "neutral"

class PodcastRequest(BaseModel):
    title: Optional[str] = "VibeVoice Podcast"
    speakers: Optional[List[SpeakerConfig]] = []
    script: str
    language: Optional[str] = "tr"
    temperature: Optional[float] = 0.7
    bg_music: Optional[str] = "lofi"

# GPU Durumu ve Model Yönetimi
CUDA_AVAILABLE = False
DEVICE_NAME = "CPU"
MODEL_LOADED = False
model = None
tokenizer = None

try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        DEVICE_NAME = torch.cuda.get_device_name(0)
except Exception:
    pass

def load_vibevoice():
    global MODEL_LOADED, model, tokenizer
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_id = os.environ.get("VIBEVOICE_MODEL_ID", "microsoft/VibeVoice-1.5B")
        print(f"[{time.strftime('%X')}] VibeVoice modeli yükleniyor ({DEVICE_NAME}): {model_id}")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if CUDA_AVAILABLE else torch.float32,
            device_map="auto" if CUDA_AVAILABLE else None
        )
        MODEL_LOADED = True
        print(f"[{time.strftime('%X')}] Model GPU'ya başarıyla yüklendi!")
    except Exception as e:
        print(f"[UYARI] VibeVoice modeli doğrudan yüklenemedi: {e}")
        MODEL_LOADED = False

@app.on_event("startup")
async def startup_event():
    if os.environ.get("AUTO_LOAD_MODEL", "false").lower() == "true":
        load_vibevoice()

@app.get("/")
@app.get("/health")
def health_check():
    """GPU sunucusunun canlılık ve donanım durumunu döner."""
    return {
        "status": "online",
        "service": "VibeVoice GPU Podcast Engine",
        "cuda_available": CUDA_AVAILABLE,
        "device": DEVICE_NAME,
        "model_loaded": MODEL_LOADED,
        "active_endpoints": ["/api/generate-podcast", "/health"]
    }

@app.post("/api/generate-podcast")
async def generate_podcast(req: PodcastRequest):
    """
    Gerçek zamanlı çok konuşmacılı senaryoyu sentezler ve ses akışı (audio/wav veya audio/mpeg) döndürür.
    """
    print(f"[{time.strftime('%X')}] Yeni podcast üretim isteği alındı: '{req.title}', Karakter sayısı: {len(req.script)}")
    
    lines = [l.strip() for l in req.script.split("\n") if l.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Senaryo metni boş olamaz.")

    # 1. Edge-TTS Türkçe Neural Motoru (Yüklüyse stüdyo kalitesinde gerçek Türkçe ses üretir)
    try:
        import edge_tts
        combined_audio = io.BytesIO()

        for line in lines:
            speaker_name = "Mert"
            text_content = line
            if line.startswith("[") and "]:" in line:
                parts = line.split("]:", 1)
                speaker_name = parts[0].replace("[", "").strip()
                text_content = parts[1].strip()

            voice = TURKISH_VOICES.get(speaker_name, "tr-TR-AhmetNeural")
            communicate = edge_tts.Communicate(text_content, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    combined_audio.write(chunk["data"])

        combined_audio.seek(0)
        return StreamingResponse(
            combined_audio,
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'inline; filename="vibevoice_turkish_podcast.mp3"'}
        )
    except ImportError:
        pass

    # 2. VibeVoice GPU Modeli
    if MODEL_LOADED and model is not None:
        import torch
        import soundfile as sf
        
        inputs = tokenizer(req.script, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_audio = model.generate(
                **inputs,
                max_new_tokens=4096,
                temperature=req.temperature
            )
        
        buf = io.BytesIO()
        sf.write(buf, output_audio.cpu().numpy(), samplerate=24000, format="WAV")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="audio/wav",
            headers={"Content-Disposition": 'inline; filename="vibevoice_gpu_podcast.wav"'}
        )

    # 3. Model henüz hazır değilse 503 Service Unavailable yerine açıklayıcı yanıt
    raise HTTPException(
        status_code=503,
        detail="VibeVoice GPU modeli veya Türkçe ses motoru (edge-tts / transformers) henüz sunucuda başlatılmadı. Lütfen sunucuda 'pip install edge-tts' veya AUTO_LOAD_MODEL=true yapın."
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"VibeVoice GPU Sunucusu başlatılıyor: http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
