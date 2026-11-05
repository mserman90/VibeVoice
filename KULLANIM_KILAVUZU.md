# Microsoft VibeVoice - Türkçe Kullanım Kılavuzu ve Geliştirici Rehberi

Bu belge, Microsoft Research tarafından geliştirilen açık kaynaklı **VibeVoice** ses yapay zekası (Voice AI) çatı ve modellerinin Türkçe kullanım rehberidir.

---

## 📑 İçindekiler
1. [VibeVoice Nedir?](#1-vibevoice-nedir)
2. [Öne Çıkan Yetenekler](#2-öne-çıkan-yetenekler)
3. [Model Mimarisi](#3-model-mimarisi)
4. [Sistem ve Donanım Gereksinimleri](#4-sistem-ve-donanım-gereksinimleri)
5. [Kurulum Adımları](#5-kurulum-adımları)
6. [Metinden Sese (TTS) Kullanımı](#6-metinden-sese-tts-kullanımı)
7. [Çok Konuşmacılı Podcast Üretimi](#7-çok-konuşmacılı-podcast-üretimi)
8. [Ses Tanıma ve Transkripsiyon (ASR)](#8-ses-tanıma-ve-transkripsiyon-asr)
9. [Parametreler ve İpuçları](#9-parametreler-ve-ipuçları)
10. [Sıkça Sorulan Sorular (SSS)](#10-sıkça-sorulan-sorular-sss)

---

## 1. VibeVoice Nedir?
**VibeVoice**, metin girdilerinden uzun soluklu, yüksek kaliteli, duygusal ve çok konuşmacılı sesler üretebilen açık kaynaklı bir ses model ailesidir. Geleneksel TTS modellerinin aksine:
* **90 dakikaya kadar** kesintisiz tek parça ses üretebilir.
* **4 farklı konuşmacıyı** aynı oturumda, konuşmacı kimliğini ve ses tonunu bozmadan seslendirebilir.
* Konuşmacıların sıra alma (turn-taking) dinamiklerini, gülme, nefes alma ve spontane tonlamalarını doğal biçimde yansıtır.

---

## 2. Öne Çıkan Yetenekler
| Özellik | VibeVoice | Geleneksel TTS |
| :--- | :--- | :--- |
| **Maksimum Üretim Süresi** | 90 Dakika | 15 - 60 Saniye |
| **Eşzamanlı Konuşmacı** | 4 Farklı Karakter | 1 - 2 Karakter |
| **Kare Hızı (Tokenizer)** | **7.5 Hz** (Ultra düşük) | 50 - 100 Hz |
| **Duygusal İfade** | Spontane gülme, tonlama, şarkı | Düz/robotik okuma |
| **ASR (Konuşma Tanıma)** | 60 dk tek parça + Diarization | Kısa parçalama gerektirir |

---

## 3. Model Mimarisi
VibeVoice üç temel ayaktan oluşur:
1. **7.5 Hz Sürekli Konuşma Tokenizer'ı:** Akustik ve anlamsal bilgiyi çok düşük bir kare hızıyla (7.5 Hz) sıkıştırarak bellek tüketimini ciddi oranda düşürür.
2. **Büyük Dil Modeli (LLM):** Diyaloğun bağlamını, kimin ne zaman konuştuğunu ve hangi duyguyla cevap verdiğini anlamlandırır.
3. **Next-Token Difüzyon Başlığı (Diffusion Head):** LLM'den gelen gizli temsilleri stüdyo kalitesinde gerçekçi ses dalgalarına dönüştürür.

---

## 4. Sistem ve Donanım Gereksinimleri
* **İşletim Sistemi:** Linux (Ubuntu 20.04/22.04) veya Windows 11 (WSL2 önerilir)
* **Python:** 3.10 veya 3.11
* **GPU (Ekran Kartı):**
  * `VibeVoice-Realtime-0.5B` için: Minimum **8 GB VRAM** (RTX 3060, RTX 4060 vb.)
  * `VibeVoice-1.5B` için: Minimum **16 - 24 GB VRAM** (RTX 3090, RTX 4090, A10G vb.)
* **RAM:** 16 GB veya üzeri (Önerilen: 32 GB)

---

## 5. Kurulum Adımları

### 1. Depoyu klonlayın ve sanal ortam oluşturun:
```bash
git clone https://github.com/microsoft/VibeVoice.git
cd VibeVoice

python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\Activate.ps1
```

### 2. Bağımlılıkları yükleyin:
```bash
# CUDA 12.1 destekli PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Ek kütüphaneler
pip install transformers diffusers accelerate soundfile librosa huggingface_hub
```

---

## 6. Metinden Sese (TTS) Kullanımı

```python
import torch
import soundfile as sf
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "microsoft/VibeVoice-1.5B"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

text = "Merhaba! VibeVoice yapay zeka ses sentezleme teknolojisi ile oluşturulmuş bir örnektir."
inputs = tokenizer(text, return_tensors="pt").to("cuda")

with torch.no_grad():
    audio = model.generate(**inputs, max_new_tokens=1024)

sf.write("cikti.wav", audio.cpu().numpy(), 24000)
```

---

## 7. Çok Konuşmacılı Podcast Üretimi

VibeVoice etiketli diyalog metinlerini doğrudan destekler:

```python
dialogue = """
[Konuşmacı 1]: Bugün yapay zeka modellerinin ses sentezindeki yeni sınırlarını konuşuyoruz.
[Konuşmacı 2]: Evet, özellikle birden fazla konuşmacının aynı anda sohbet ettiği podcast formatları inanılmaz bir seviyeye ulaştı.
[Konuşmacı 1]: [gülerek] Kesinlikle! Artık robotik sesler geride kaldı.
"""

inputs = tokenizer(dialogue, return_tensors="pt").to("cuda")
with torch.no_grad():
    podcast_audio = model.generate(**inputs, max_new_tokens=4096, temperature=0.7)

sf.write("podcast.wav", podcast_audio.cpu().numpy(), 24000)
```

---

## 8. Ses Tanıma ve Transkripsiyon (ASR)

VibeVoice-ASR ile ses dosyasındaki konuşmacıları ve zaman damgalarını ayrıştırarak metne dökebilirsiniz:

```python
from transformers import pipeline

asr_pipeline = pipeline("automatic-speech-recognition", model="microsoft/VibeVoice-ASR", device="cuda:0")
transcription = asr_pipeline("kayit.mp3", return_timestamps=True)

for segment in transcription["chunks"]:
    spk = segment.get("speaker", "Bilinmeyen")
    start, end = segment["timestamp"]
    text = segment["text"]
    print(f"[{start:.2f}s - {end:.2f}s] {spk}: {text}")
```

---

## 9. Parametreler ve İpuçları
* **Duygu Etiketleri:** Metin aralarına `[gülerek]`, `[şaşkınlıkla]`, `[düşünceli]` gibi parantez içi ifadeler ekleyerek tonlama zenginliği sağlayabilirsiniz.
* **Temperature:**
  * `0.3 - 0.5`: Resmi metinler, belgesel seslendirmeleri.
  * `0.7 - 0.8`: Doğal diyaloglar, podcast sohbetleri.
* **Bellek Tasarrufu:** Uzun çıktılarda `bfloat16` veya `float16` hassasiyeti ve FlashAttention kullanılması önerilir.

---

## 10. Sıkça Sorulan Sorular (SSS)
* **Soru: VibeVoice GitHub Pages üzerinde canlı model çalıştırabilir mi?**  
  **Cevap:** Hayır, GitHub Pages yalnızca statik web sayfalarını barındırır. Modelin çalışması için GPU sunucusu gereklidir. Web stüdyosu doğrudan GPU sunucunuzdaki API uç noktasına bağlanarak çalışır.
* **Soru: Türkçe dil desteği var mı?**  
  **Cevap:** Evet. Web stüdyosu hem tarayıcı içi doğal Türkçe ses motoruyla sıfır gecikmeyle çalışabilir hem de GPU sunucusundaki Türkçe Neural sesleri destekler.

---

## 11. GPU Sunucusunda API Başlatma ve Web Stüdyosuna Bağlama

Kendi yerel GPU makinenizde veya bulut sunucunuzda (RunPod, AWS, Colab vb.) API'yi başlatmak için:

### 1. Sunucu Gereksinimlerini Yükleyin:
```bash
pip install fastapi uvicorn torch transformers soundfile edge-tts
```

### 2. API Sunucusunu Çalıştırın:
```bash
# VibeVoice GPU modelini otomatik yüklemek için:
export AUTO_LOAD_MODEL=true  # Windows PowerShell: $env:AUTO_LOAD_MODEL="true"
python server.py
```
Sunucu varsayılan olarak `http://0.0.0.0:8000` adresinde ayağa kalkar.

### 3. Web Stüdyosuna Bağlayın:
1. [Web Podcast Stüdyosu](https://mserman90.github.io/VibeVoice/) adresini açın.
2. Sayfanın üstündeki **"VibeVoice GPU API Uç Noktası"** kutusuna sunucu adresinizi yazın:
   * Yerel makine için: `http://localhost:8000`
   * Uzak sunucu için (ngrok veya public IP): `https://xyz.ngrok-free.app`
3. **"Sına & Bağlan"** butonuna tıklayın. Durum rozeti `🟢 Online (CUDA: RTX ...)` olduğunda, senaryonuzu yazıp **"⚡ VibeVoice GPU Sentezi"** butonuna basarak doğrudan GPU'dan ses üretebilirsiniz!

