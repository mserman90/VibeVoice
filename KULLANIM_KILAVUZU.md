# PodcastLab: Kullanım Kılavuzu & Geliştirici Rehberi

Bu belge, Microsoft Research tarafından geliştirilen **VibeVoice** ses yapay zekası (Voice AI) mimarisini temel alan, çok konuşmacılı Türkçe podcast üretim stüdyosu **PodcastLab** için kapsamlı kullanım ve geliştirici rehberidir.

---

## 📑 İçindekiler
1. [PodcastLab Nedir?](#1-podcastlab-nedir)
2. [Öne Çıkan Yetenekler](#2-öne-çıkan-yetenekler)
3. [Çift Motorlu Mimari (Dual-Engine)](#3-çift-motorlu-mimari-dual-engine)
4. [PodcastLab Stüdyosu Nasıl Kullanılır?](#4-podcastlab-stüdyosu-nasıl-kullanılır)
5. [Türkçe Ses Motorları & Sistem Kurulumu](#5-türkçe-ses-motorları--sistem-kurulumu)
6. [Tarayıcı Optimizasyonları (Edge & Chrome)](#6-tarayıcı-optimizasyonları-edge--chrome)
7. [Yerel / GPU Sunucusu Kurulumu (`server.py`)](#7-yerel--gpu-sunucusu-kurulumu-serverpy)
8. [HTTPS & Tünelleme Rehberi (Cloudflare / ngrok)](#8-https--tünelleme-rehberi-cloudflare--ngrok)
9. [Transkript ve Altyazı Dışa Aktarma](#9-transkript-ve-altyazı-dışa-aktarma)
10. [Sıkça Sorulan Sorular (SSS)](#10-sıkça-sorulan-sorular-sss)

---

## 1. PodcastLab Nedir?
**PodcastLab**, metin girdilerini profesyonel radyo ve podcast kalitesinde, çok konuşmacılı, duygu vurgulu ve arka plan müzikli bir ses prodüksiyonuna dönüştüren modern bir yapay zeka stüdyosudur.

* **4 Farklı Karakter:** Mert (Derin Bas), Selin (Canlı Soprano), Can (Sıcak Tenor) ve Deniz (Dengeli Nötr).
* **Duygu & İfade Etiketleri:** `[gülerek]`, `[şaşkınlıkla]`, `[şarkı söyler gibi]`, `[düşünceli]`, `[heyecanlı]` gibi duygu geçişleri.
* **Arka Plan Müzik Mikseri:** Lo-Fi Beats, Chillhop, Jazz Lounge ve Ambient müzik akışları.
* **Senkron Transkript ve Dalga Biçimi:** Konuşulan cümlenin canlı sarı vurgulanması ve gerçek zamanlı frekans görselleştirmesi.

---

## 2. Öne Çıkan Yetenekler
| Özellik | PodcastLab Stüdyo | Geleneksel TTS Araçları |
| :--- | :--- | :--- |
| **Konuşmacı Sayısı** | **4 Eşzamanlı Karakter** (Mert, Selin, Can, Deniz) | Tek veya kısıtlı 1-2 ses |
| **Duygusal İfade** | `[gülerek]`, `[şaşkınlıkla]`, `[düşünceli]` vb. | Düz, robotik tonlama |
| **Çalışma Modu** | **Sıfır Kurulum Web Motoru** + **Harici GPU API** | Sadece sunucu bağımlı |
| **Arka Plan Müziği** | Dahili Lo-Fi, Chillhop, Jazz mikseri | Yok veya harici yazılım gerektirir |
| **Dışa Aktarma** | Ses (.wav/.mp3), Altyazı (.srt) ve Transkript (.txt) | Yalnızca ham ses |

---

## 3. Çift Motorlu Mimari (Dual-Engine)
1. **Dahili Web Motoru (WebSpeech API + Web Audio):** Herhangi bir kurulum veya GPU sunucusuna ihtiyaç duymadan, doğrudan tarayıcınızın donanım ivmeli Türkçe ses motorlarını kullanarak sıfır gecikmeyle çalışır.
2. **VibeVoice GPU Sunucu Entegrasyonu (`server.py`):** Kendi GPU makinenizde veya bulutta çalışan FastAPI arka ucu üzerinden stüdyo kalitesinde difüzyon tabanlı üretim sağlar.

> **💡 Pop-Up'sız Akıcı Geçiş (Seamless Fallback):** Eğer GPU sunucusu kapalıysa veya ulaşılamaz durumdaysa, uygulama ekrana rahatsız edici hata pencereleri çıkarmak yerine otomatik ve sessizce Dahili Web Motoru'na geçerek podcast'inizi kesintisiz olarak oynatır.

---

## 4. PodcastLab Stüdyosu Nasıl Kullanılır?

### Senaryo Formatı
Senaryo kutusuna konuşmacı isimlerini köşeli parantez içinde belirterek diyaloglarınızı yazın:

```text
[Mert]: Herkese merhaba! PodcastLab stüdyosuna hoş geldiniz.
[Selin]: [heyecanlı] Selam Mert! Bugün ses yapay zekasındaki son gelişmeleri konuşuyoruz.
[Can]: [gülerek] Evet, artık robotik sesler geride kaldı; doğal sohbetler yapabiliyoruz!
[Deniz]: [düşünceli] Özellikle farklı tonlamaların tek oturumda birleşmesi harika.
```

---

## 5. Türkçe Ses Motorları & Sistem Kurulumu

### Windows 11 / 10 Kullanıcıları İçin (Microsoft Ahmet & Emel):
1. Windows **Ayarlar** (Settings) uygulamasını açın (`Win + I`).
2. **Zaman ve Dil** > **Konuşma** sekmesine gidin.
3. **"Ses ekle"** butonuna tıklayın ve **Türkçe (Türkiye)** paketini yükleyin.
4. Bu işlem ile sisteminize doğal *Microsoft Ahmet* ve *Microsoft Emel* sesleri dahil edilir.

### Apple macOS & iOS Kullanıcıları İçin:
Sistem Ayarları > Erişilebilirlik > Seslendirme > Sesler menüsünden **Yelda (Gelişmiş)** veya **Tolga (Gelişmiş)** profillerini indirebilirsiniz.

---

## 6. Tarayıcı Optimizasyonları (Edge & Chrome)

* **Microsoft Edge (Önerilen):** Microsoft'un bulut tabanlı doğal nöral seslerini (*Microsoft Ahmet Online*, *Microsoft Emel Online*) yerel olarak destekler. Karakterler en üst düzey akıcılık ve doğal nefes vurgularıyla konuşur.
* **Google Chrome (Genişletilmiş Perde):** Chrome standart olarak tek bir *Google Türkçe* sesi sağlar. PodcastLab, 4 karakteri birbirinden net bir şekilde ayırmak için genişletilmiş akustik perde (pitch) katsayıları uygular:
  * **Mert:** 0.52 (Derin Bas)
  * **Selin:** 1.62 (Canlı Soprano)
  * **Can:** 1.16 (Sıcak Tenor)
  * **Deniz:** 0.82 (Dengeli Nötr)

---

## 7. Yerel / GPU Sunucusu Kurulumu (`server.py`)

Kendi bilgisayarınızdaki ekran kartını (CUDA) veya uzak bir GPU sunucusunu kullanmak için:

```bash
# 1. Gerekli kütüphaneleri yükleyin
pip install fastapi uvicorn torch transformers soundfile edge-tts pydantic

# 2. Sunucuyu başlatın
python server.py
```
Sunucu varsayılan olarak `http://0.0.0.0:8000` adresinde ayağa kalkar.

---

## 8. HTTPS & Tünelleme Rehberi (Cloudflare / ngrok)

GitHub Pages güvenli **HTTPS** (`https://mserman90.github.io`) üzerinden yayın yaptığı için, yerel `http://localhost:8000` adresine yapılacak çağrılar tarayıcılar tarafından *Mixed Content / Karışık İçerik* sebebiyle engellenebilir. 

Bunu çözmek için yerel sunucunuzu güvenli bir HTTPS tüneline bağlayabilirsiniz:

### Yöntem 1: Cloudflare Tunnel (Önerilen & Ücretsiz)
```bash
cloudflared tunnel --url http://localhost:8000
```
Terminalde verilen `https://ornek-alan.trycloudflare.com` adresini stüdyodaki **GPU Uç Noktası** kutusuna yapıştırın.

### Yöntem 2: ngrok
```bash
ngrok http 8000
```
Oluşan `https://xyz.ngrok-free.app` adresini stüdyoya girin.

---

## 9. Transkript ve Altyazı Dışa Aktarma
* **Metin Transkripti (`.txt`):** Konuşma sırasına göre formatlanmış temiz metin transkripti.
* **Altyazı Dosyası (`.srt`):** Video kurgu yazılımları (Premiere, DaVinci Resolve) ve video oynatıcılar için zaman damgalı senkron altyazı.
* **Ses Dosyası (`.wav` / `.mp3`):** Üretilen podcast kaydı.

---

## 10. Sıkça Sorulan Sorular (SSS)

**S: "GPU Sunucusuna Bağlanılamadı (Failed to fetch)" hatası neden olur?**  
C: Bu durum yerel `server.py` dosyasının çalışmadığını veya HTTPS güvenlik kısıtlamasına takıldığını gösterir. PodcastLab'in güncel sürümünde bu durum otomatik algılanır ve pop-up çıkarmadan anında dahili Türkçe motoruna geçer.

**S: Arka plandaki parazit/vınlama sesi nasıl çözüldü?**  
C: Eski sürümdeki sentetik Web Audio sinüs osilatörleri tamamen kaldırıldı; sadece temiz Lo-Fi ve Chillhop ambiyans akışları entegre edildi.

---

**© 2026 PodcastLab · Microsoft Research VibeVoice Topluluk Geliştirmesi**  
*Canlı Stüdyo:* [https://mserman90.github.io/VibeVoice/](https://mserman90.github.io/VibeVoice/)  
*Web Kılavuzu:* [https://mserman90.github.io/VibeVoice/kilavuz.html](https://mserman90.github.io/VibeVoice/kilavuz.html)
