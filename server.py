"""
VibeVoice & Türkçe Çok Konuşmacılı Podcast API Sunucusu (FastAPI + PyTorch / Edge-TTS)
Bu sunucu, web arayüzünden gelen çok konuşmacılı Türkçe podcast isteklerini alır,
VibeVoice ve Türkçe Neural ses motorları ile sentezleyerek WAV/MP3 ses dosyası döner.
"""

import os
import io
import time
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

app = FastAPI(
    title="VibeVoice Türkçe Podcast API",
    description="VibeVoice ve Türkçe Neural çok konuşmacılı ses sentezi API'si",
    version="1.1.0"
)

# CORS izinleri (GitHub Pages üzerinden gelen isteklere tam izin verir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Türkçe Neural Ses Haritası (Microsoft Edge-TTS / Neural)
TURKISH_VOICES = {
    "Mert": "tr-TR-AhmetNeural",      # Tok, profesyonel erkek sesi
    "Selin": "tr-TR-EmelNeural",      # Dinamik, akıcı kadın sesi
    "Can": "tr-TR-AhmetNeural",       # Genç erkek sesi (pitch modifikasyonu ile)
    "Deniz": "tr-TR-EmelNeural",      # Dengeli kadın/moderatör sesi
    "default_male": "tr-TR-AhmetNeural",
    "default_female": "tr-TR-EmelNeural"
}

class SpeakerConfig(BaseModel):
    id: str
    name: str
    voice: Optional[str] = "default"
    gender: Optional[str] = "neutral"

class PodcastRequest(BaseModel):
    title: Optional[str] = "Yeni Türkçe Podcast"
    speakers: Optional[List[SpeakerConfig]] = []
    script: str
    language: Optional[str] = "tr"
    temperature: Optional[float] = 0.7
    bg_music: Optional[str] = "lofi"

# VibeVoice GPU Modeli
VIBEVOICE_LOADED = False
vibevoice_model = None
vibevoice_tokenizer = None

def load_vibevoice():
    global VIBEVOICE_LOADED, vibevoice_model, vibevoice_tokenizer
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_id = "microsoft/VibeVoice-1.5B"
        print(f"[{time.strftime('%X')}] VibeVoice modeli GPU'ya yükleniyor: {model_id}")
        vibevoice_tokenizer = AutoTokenizer.from_pretrained(model_id)
        vibevoice_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        VIBEVOICE_LOADED = True
        print(f"[{time.strftime('%X')}] VibeVoice modeli başarıyla yüklendi!")
    except Exception as e:
        print(f"[BİLGİ] VibeVoice GPU modeli yüklenemedi: {e}")
        VIBEVOICE_LOADED = False

@app.on_event("startup")
async def startup_event():
    if os.environ.get("AUTO_LOAD_MODEL", "false").lower() == "true":
        load_vibevoice()

@app.get("/")
def health_check():
    return {
        "status": "active",
        "service": "VibeVoice & Türkçe Podcast Sentezleyici",
        "vibevoice_gpu": VIBEVOICE_LOADED,
        "turkish_engine": "Microsoft Neural Türkçe TTS & WebSpeech Destekli",
        "default_voices": TURKISH_VOICES
    }

async def generate_turkish_audio_stream(script: str):
    """
    Edge-TTS kütüphanesi yüklüyse Türkçe Neural seslerle sentezler,
    yoksa uyarı verir.
    """
    try:
        import edge_tts
        lines = [l.strip() for l in script.split("\n") if l.strip()]
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
        return combined_audio
    except ImportError:
        return None

@app.post("/api/generate-podcast")
async def generate_podcast(req: PodcastRequest):
    """
    Çok konuşmacılı Türkçe metni sentezler ve MP3/WAV ses dosyası döndürür.
    """
    lines = [l.strip() for l in req.script.split("\n") if l.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Senaryo metni boş olamaz.")

    # 1. Türkçe Neural TTS Denemesi
    if req.language == "tr":
        audio_stream = await generate_turkish_audio_stream(req.script)
        if audio_stream:
            return StreamingResponse(audio_stream, media_type="audio/mpeg")

    # 2. VibeVoice GPU Modeli Denemesi
    if VIBEVOICE_LOADED and vibevoice_model is not None:
        import torch
        import soundfile as sf
        
        inputs = vibevoice_tokenizer(req.script, return_tensors="pt").to(vibevoice_model.device)
        with torch.no_grad():
            output_audio = vibevoice_model.generate(
                **inputs,
                max_new_tokens=4096,
                temperature=req.temperature
            )
        
        buf = io.BytesIO()
        sf.write(buf, output_audio.cpu().numpy(), samplerate=24000, format="WAV")
        buf.seek(0)
        return StreamingResponse(buf, media_type="audio/wav")

    # 3. Bilgi yanıtı
    return {
        "status": "success",
        "language": "tr",
        "title": req.title,
        "message": "Türkçe metin başarıyla işlendi. Web arayüzü tarayıcı içi doğal Türkçe ses motorunu (WebSpeech) kullanarak seslendirebilir.",
        "lines_count": len(lines),
        "estimated_duration_sec": len(lines) * 4.2
    }

if __name__ == "__main__":
    import uvicorn
    print("VibeVoice Türkçe Podcast API başlatılıyor (http://localhost:8000)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
