"""
VibeVoice Webhook & API Sunucusu (FastAPI + PyTorch)
Bu sunucu, web arayüzünden gelen çok konuşmacılı podcast isteklerini alır,
VibeVoice modeli ile sentezler ve ses dosyasını döner.
"""

import os
import io
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

app = FastAPI(
    title="VibeVoice Podcast API",
    description="VibeVoice çok konuşmacılı ses sentezi API'si",
    version="1.0.0"
)

# CORS izinleri (GitHub Pages üzerinden gelen isteklere izin verir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SpeakerConfig(BaseModel):
    id: str
    name: str
    voice: Optional[str] = "default"
    gender: Optional[str] = "neutral"

class PodcastRequest(BaseModel):
    title: Optional[str] = "Yeni Podcast"
    speakers: List[SpeakerConfig]
    script: str
    temperature: Optional[float] = 0.7
    bg_music: Optional[str] = "none"

# Model yükleme durumu
MODEL_LOADED = False
model = None
tokenizer = None

def load_vibevoice():
    global MODEL_LOADED, model, tokenizer
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_id = "microsoft/VibeVoice-1.5B"
        print(f"[{time.strftime('%X')}] VibeVoice modeli yükleniyor: {model_id}")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        MODEL_LOADED = True
        print(f"[{time.strftime('%X')}] Model başarıyla GPU'ya yüklendi!")
    except Exception as e:
        print(f"[UYARI] Gerçek GPU modeli yüklenemedi (CUDA/Bellek kontrol edin): {e}")
        MODEL_LOADED = False

@app.on_event("startup")
async def startup_event():
    # Arka planda GPU varsa modeli yüklemeyi dener
    if os.environ.get("AUTO_LOAD_MODEL", "false").lower() == "true":
        load_vibevoice()

@app.get("/")
def health_check():
    return {
        "status": "active",
        "service": "VibeVoice Podcast Generator API",
        "model_loaded": MODEL_LOADED,
        "device": "CUDA" if MODEL_LOADED else "Mock/CPU"
    }

@app.post("/api/generate-podcast")
async def generate_podcast(req: PodcastRequest):
    """
    Çok konuşmacılı metni VibeVoice ile sentezleyerek WAV/MP3 ses dosyası ve transkript döndürür.
    """
    print(f"Podcast üretim isteği alındı: '{req.title}', Konuşmacılar: {len(req.speakers)}")
    
    # 1. Senaryoyu ayrıştır
    lines = [l.strip() for l in req.script.split("\n") if l.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Senaryo metni boş olamaz.")

    # 2. Model yüklü ise gerçek VibeVoice çıkarımı (Inference)
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
        
        buffer = io.BytesIO()
        sf.write(buffer, output_audio.cpu().numpy(), samplerate=24000, format="WAV")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="audio/wav")
    
    # 3. Model henüz sunucuda hazır değilse veya geliştirme modundaysa bilgi döner
    return {
        "status": "success",
        "message": "Metin başarıyla işlendi. (GPU ortamında gerçek inference için AUTO_LOAD_MODEL=true yapın)",
        "title": req.title,
        "speakers_count": len(req.speakers),
        "lines_count": len(lines),
        "estimated_duration_sec": len(lines) * 4.5
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
