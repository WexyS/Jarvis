# J.A.R.V.I.S v2.0 — Kullanım Kılavuzu

Kişisel, yerel çalışan çoklu-agent yapay zeka asistanı. FastAPI + React/Tauri GUI + Ollama.

---

## Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 18+ (GUI için)
- Ollama (LLM runtime)

### Adımlar

```bash
# 1. Sanal ortam oluştur ve aktive et
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 2. Bağımlılıkları yükle
pip install -e ".[dev]"

# 3. Ollama'yı kur ve model indir
ollama pull qwen2.5:14b

# 4. .env dosyasını oluştur
cp .env.example .env
# .env dosyasını düzenle (API key'ler opsiyonel)

# 5. Backend'i başlat
python -m uvicorn jarvis.api.main:app --host 127.0.0.1 --port 8000

# 6. GUI'yi başlat (opsiyonel)
cd jarvis-desktop && npm install && npm run dev
```

### Hızlı Başlatma

```bash
# Tek tuşla başlatma (Windows)
start-jarvis-desktop.bat
```

---

## Ajanlar ve Komutlar

### 🤖 Mevcut Ajanlar

| Ajan | Açıklama | Örnek Komutlar |
|------|----------|----------------|
| **CoderAgent** | Kod yazma, debug, çalıştırma | "Python ile fibonacci yaz" |
| **ResearcherAgent** | Web araştırması, sentez | "Quantum computing nedir?" |
| **RPAOperatorAgent** | Bilgisayar kontrolü | "Chrome'u aç" |
| **EmailAgent** | E-posta okuma, özetleme, gönderme | "Maillerimi özetle" |
| **SystemMonitorAgent** | CPU/RAM/disk izleme | "Sistem durumu nedir?" |
| **ClipboardAgent** | Pano analizi | "Panodaki kodu analiz et" |
| **MeetingAgent** | Toplantı kaydı ve transkripsiyon | "Toplantıyı kaydet" |
| **FileOrganizerAgent** | Dosya düzenleme | "İndirilenleri düzenle" |

### E-posta Ajanı
```
"emaillerimi oku"          → Son 10 email listele
"sabah özeti"              → En önemli 5 emaili özetle
"ahmet'e şunu yaz"         → Taslak oluştur
"gönder"                   → Taslağı gönder
```

### Meeting Ajanı
```
"toplantıyı kaydet"        → Mikrofonu başlat
"toplantıyı durdur"        → Kaydı durdur, transkribe et
"özet çıkar"              → Özet + aksiyon öğeleri
```

### File Organizer
```
"masaüstünü düzenle"       → Desktop dosyalarını kategorize et
"yinelenen dosyaları bul"  → Duplicate tespiti
"indirilenleri düzenle"    → Downloads klasörünü organize et
```

---

## Memory Sistemi

Jarvis 3 katmanlı bellek mimarisi kullanır:

### 1. Working Memory (Kısa Süreli)
- Son 20 mesajı tutar (deque)
- Token sınırı: 4000 token
- Aşıldığında otomatik özetleme

### 2. Long-Term Memory (Uzun Süreli)
- **SQLite + FTS5**: Metin tabanlı arama
- **ChromaDB**: Vektör tabanlı semantik arama
- **Hibrit arama**: RRF (Reciprocal Rank Fusion) ile birleştirme
- **Decay**: 90 günden eski, önemsiz bilgiler unutulur
- **Consolidation**: Gece 03:00'te otomatik konsolidasyon

### 3. Procedural Memory (Stratejiler)
- Başarılı görev tamamlama pattern'leri
- Exponential moving average ile başarı oranı
- Benzer görevlerde en iyi strateji önerilir

---

## Konfigürasyon

### config/agents.yaml
Her ajanın ayarları bu dosyada tanımlanır:

```yaml
agents:
  email:
    check_interval_minutes: 30
    max_emails_summary: 5
  sysmon:
    poll_interval_seconds: 5
    alert_thresholds:
      cpu_percent: 85
  meeting:
    whisper_model: "base"
    language: "tr"
```

### .env Değişkenleri
```
JARVIS_EMAIL_USER=your@email.com
JARVIS_EMAIL_PASS=your_app_password
JARVIS_API_KEY=optional_api_key     # API koruması için
OLLAMA_BASE_URL=http://localhost:11434
```

### İsteğe Bağlı API Key'ler
`.env.example` dosyasında tüm desteklenen LLM sağlayıcıları listelenir.
Hiçbiri zorunlu değildir — varsayılan olarak Ollama kullanılır.

---

## API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/health` | GET | Sağlık kontrolü |
| `/` | GET | API bilgileri |
| `/chat` | POST | Sohbet endpointi |
| `/agents` | GET | Ajan listesi |
| `/status` | GET | Sistem durumu |

### Rate Limiting
- `/health`: 60 istek/dakika
- `/chat`: 30 istek/dakika
- Aşıldığında `429 Too Many Requests` döner

### API Key Koruma (Opsiyonel)
`.env`'de `JARVIS_API_KEY` tanımlıysa:
```
X-API-Key: your_secret_key
```
header'ı zorunludur.

---

## Test Çalıştırma

```bash
pytest tests/ -v --cov=jarvis
```

---

## Lisans

MIT License — Copyright (c) 2025 WexyS
