# Jarvis v2.0 — Kullanım Kılavuzu

> **Son güncelleme:** 11 Nisan 2026
> **Model:** Qwen 2.5 14B (yerel) + Claude Sonnet 4 (OpenRouter, ücretsiz)
> **Mimari:** Multi-Agent (Coder, Researcher, RPA) + Voice Pipeline + GUI

---

## Hızlı Başlangıç

```bash
cd C:\Users\nemes\Desktop\Jarvis
python -m jarvis.cli
```

Animasyonlu Mark-XXXV GUI açılır. Hem **sesli** hem **yazılı** iletişim kurabilirsin.

---

## 🖥️ GUI Kullanımı

```
┌────────────────────────────────────────────────────────┐
│  J.A.R.V.I.S         Qwen 2.5 14B + Claude            │
│  Just A Rather Very Intelligent System                 │
├────────────────────────────────────────────────────────┤
│          ╭──────────────────────────────╮              │
│          │     Animasyonlu Orb           │              │
│          │  (dönen halkalar, pulse)      │              │
│          ╰──────────────────────────────╯              │
│                                                        │
│  ● DİNLİYOR                                            │
│  ▂▃▅▆▇▆▅▃▂▁▂▃▅▆▇▆▅▃▂▁   (ses dalgası)                │
│                                                        │
├────────────────────────────────────────────────────────┤
│  Log alanı:                                            │
│  You: /code hackernews başlıklarını JSON kaydet       │
│  Jarvis: [Python kodu yazıldı, çalıştırıldı]           │
├────────────────────────────────────────────────────────┤
│  [Bir mesaj yazın...]        [GÖNDER ▸]                │
│  [🎙 LIVE]                        [F4] SUSTUR           │
└────────────────────────────────────────────────────────┘
```

### Durum Göstergeleri

| Gösterge | Anlamı |
|----------|--------|
| `● DİNLİYOR` | Mikrofon açık, ses bekleniyor |
| `⟳ YAZIYA ÇEVRİLİYOR` | Ses → metin (STT) |
| `◈ DÜŞÜNÜYOR` | LLM yanıt üretiyor |
| `● KONUŞUYOR` | TTS sesli okuyor |
| `⊘ SUSTURULDU` | Mikrofon kapalı |

### Kontroller

| Kontrol | İşlev |
|---------|-------|
| **🎙 LIVE / 🔇 MUTED** | Mikrofon aç/kapat |
| **F4** | Mikrofon sustur/aç (klavye kısayolu) |
| **Metin kutusu + GÖNDER** | Yazarak soru sor / komut ver |
| **X butonu** | Uygulamayı kapat |

---

## 🚀 Optimizasyonlar

| Optimizasyon | Önceki | Sonraki | Kazanım |
|--------------|--------|---------|---------|
| **GUI Frame Rate** | 60fps | 30fps | CPU/GPU %50 azaldı |
| **LLM num_ctx** | 2048 | 1024 | VRAM %50 azaldı |
| **LLM num_predict** | 4096 | 1024 | Yanıt süresi %60 kısaldı |
| **Mirostat sampling** | Kapalı | Açık | Kalite arttı, tutarsızlık azaldı |
| **Lazy loading** | Eager | Arka plan thread | GUI anında açılıyor |
| **Context window** | 8 mesaj | 6 mesaj | Memory %25 azaldı |
| **Timeout** | 180s | 120s | Hızlı hata bildirimi |
| **num_gpu** | Auto | 999 | Tüm model GPU'da |

### Sistem Kaynakları

| Bileşen | RAM | VRAM | CPU |
|---------|-----|------|-----|
| **GUI (idle)** | ~50MB | ~20MB | ~2% |
| **Voice Pipeline** | ~500MB | ~1GB | ~5% |
| **qwen2.5:14b** | ~2GB | ~9GB | ~10% |
| **Toplam** | ~2.5GB | ~10GB | ~17% |

---

GUI'den bağımsız, daha güçlü mod:

```bash
python -m jarvis.v2.bootstrap
```

### Komut Prefixleri

| Prefix | Agent | Ne Yapar |
|--------|-------|----------|
| `/code <görev>` | **Coder** (qwen2.5-coder:7b) | Kod yazar, **çalıştırır**, hata varsa **kendi düzeltir** |
| `/research <konu>` | **Researcher** (qwen2.5:14b) | Web araması + içerik okuma + sentez |
| `/rpa <görev>` | **RPA Operator** | Ekran görüntüsü, OCR, mouse/klavye kontrolü |
| `/status` | — | Tüm sistem durumunu göster |
| `/quit` | — | Çıkış |

### Örnek Kullanım

```
You> /code Write a Python script that fetches titles from https://news.ycombinator.com/ and saves them to hn_titles.json
Jarvis processing...
→ Kod yazıldı: workspace/task_xxxxxxxx.py
→ Çalıştırıldı: Başarılı
→ Çıktı: Titles saved to hn_titles.json

You> /research What are the latest developments in quantum computing?
Jarvis processing...
→ Web araması yapıldı, 5 kaynak okundu
→ Özet: [detaylı yanıt]

You> /rpa Take a screenshot and read the text on screen
Jarvis processing...
→ Screenshot taken
→ OCR: "Notepad - Untitled"
```

---

## 📦 Kurulu Modeller

| Model | Boyut | VRAM | Kullanım |
|-------|-------|------|----------|
| `qwen2.5:14b` | 9GB | ~9GB | Genel chat + research |
| `qwen2.5-coder:7b` | 5GB | ~5GB | Kod yazma (özel eğitimli) |
| `qwen3:8b` | 5GB | ~5GB | Function calling |
| **OpenRouter Free** | Cloud | 0GB | 29 ücretsiz model (Claude, GPT, Llama) |

### OpenRouter Ücretsiz Modeller

API key'in varsa `openrouter/free` router'ı otomatik olarak ücretsiz modeller arasında seçim yapar:
- `arcee-ai/trinity-large-preview:free`
- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- Ve daha fazlası... **Kredi gerektirmez, tamamen bedava.**

---

## 🔧 API Anahtarları (`.env`)

```
OPENROUTER_API_KEY=sk-or-v1-xxxxx    # Claude/GPT ücretsiz erişim
OPENAI_API_KEY=sk-proj-xxxxx         # OpenAI fallback (opsiyonel)
```

**OpenRouter'dan ücretsiz API key al:**
1. `openrouter.ai` → Sign up
2. Settings → API Keys → Create key
3. `.env` dosyasına yapıştır

---

## 🧠 Mimari

```
┌──────────────────────────────────────────────────────────┐
│                    JARVIS v2.0                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  GUI (Mark-XXXV) + Voice Pipeline                   │ │
│  │  🎤 STT: Google Web Speech → Whisper (yedek)       │ │
│  │  🔊 TTS: edge-tts (tr-TR-EmelNeural)               │ │
│  └───────────────────┬────────────────────────────────┘ │
│                      │                                   │
│  ┌───────────────────▼────────────────────────────────┐ │
│  │  v2 Orchestrator                                    │ │
│  │  ┌──────────┐ ┌───────────┐ ┌─────────────────┐   │ │
│  │  │  Coder   │ │Researcher │ │  RPA Operator   │   │ │
│  │  │(coder:7b)│ │ (14b)     │ │ (14b)           │   │ │
│  │  └────┬─────┘ └─────┬─────┘ └────────┬────────┘   │ │
│  └───────┼─────────────┼────────────────┼────────────┘ │
│          │             │                │              │
│  ┌───────▼─────────────▼────────────────▼────────────┐ │
│  │          Hybrid LLM Router                         │ │
│  │  openrouter_free → ollama → openrouter (fallback) │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Memory Engine                                     │  │
│  │  ChromaDB (Vector) + NetworkX (Graph) + Lessons   │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tanılama Komutları

| Komut | Açıklama |
|-------|----------|
| `python -m jarvis.cli --list-mics` | Mikrofonları listele |
| `python -m jarvis.cli --test-mic` | Mikrofonu test et |
| `python -m jarvis.v2.bootstrap --status` | v2 sistem durumu |
| `python -m jarvis.v2.bootstrap --test-coder` | Coder Agent test |
| `python -m jarvis.v2.bootstrap --test-rpa` | RPA Agent test |
| `ollama ls` | Yüklü modelleri listele |

---

## ⚙️ Yapılandırma

### `config.yaml`
```yaml
model:
  ollama_model: "qwen2.5:14b"   # Aktif model
  ollama_base_url: "http://localhost:11434"
  max_tokens: 4096
  temperature: 0.7
  language: "tr"
```

### Ortam Değişkenleri

| Değişken | Açıklama |
|----------|----------|
| `JARVIS_MODEL` | Varsayılan model (`qwen2.5:14b`) |
| `JARVIS_STT` | STT motoru: `google` veya `whisper` |
| `JARVIS_TTS_VOICE` | TTS sesi (`tr-TR-EmelNeural`) |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OLLAMA_BASE_URL` | Ollama sunucu (`http://localhost:11434`) |

---

## 🔍 Sorun Giderme

### GUI açılmıyor / donuyor
```bash
# Ollama'yı kontrol et
ollama ls
ollama serve

# Bağımlılıkları yükle
pip install -e .
```

### Ses çıkmıyor (TTS)
```bash
pip install edge-tts pygame
```

### Mikrofon algılanmıyor
```bash
python -m jarvis.cli --list-mics
python -m jarvis.cli --test-mic
```

### "No LLM providers available" hatası
```bash
# Ollama çalışıyor mu?
ollama serve

# Model yüklü mü?
ollama pull qwen2.5:14b
```

### OpenRouter 402 hatası (kredi bitti)
Sistem otomatik olarak yerel Ollama modeline fallback yapar. Manuel kredi yüklemek istersen:
`openrouter.ai/settings/credits` → kredi ekle.

---

## 📋 Hızlı Başvuru

| İşlem | Komut |
|-------|-------|
| **GUI Başlat** | `python -m jarvis.cli` |
| **v2 Terminal** | `python -m jarvis.v2.bootstrap` |
| **Kapat** | X butonu / `/quit` |
| **Sustur** | F4 veya 🎙 butonu |
| **Model Değiştir** | `config.yaml` → `ollama_model` |
| **Sanal Ortam** | `.venv\Scripts\activate` / `deactivate` |

---

## 📁 Proje Yapısı

```
Jarvis/
├── jarvis/
│   ├── cli.py              # CLI entry point (GUI başlatır)
│   ├── gui_app.py          # Mark-XXXV Tkinter GUI
│   ├── config.py           # Yapılandırma (Pydantic)
│   ├── voice_pipeline.py   # Sesli asistan pipeline
│   ├── tts_voice.py        # TTS modülü
│   ├── memory.py           # Eski bellek sistemi
│   ├── llm.py              # Eski LLM router
│   ├── coding.py           # Eski kod asistanı
│   ├── research.py         # Eski araştırma asistanı
│   └── v2/                 # ── YENİ v2 Multi-Agent ──
│       ├── bootstrap.py    # v2 entry point
│       ├── core/
│       │   ├── orchestrator.py   # Merkezi beyin
│       │   ├── llm_router.py     # Hybrid LLM routing
│       │   ├── hermes.py         # Hermes TAO loop
│       │   ├── event_bus.py      # Pub/sub event system
│       │   └── blackboard.py     # Shared context
│       ├── agents/
│       │   ├── coder.py          # Self-healing kod agent
│       │   ├── researcher.py     # Deep research agent
│       │   └── rpa_operator.py   # Computer use agent
│       └── memory/
│           └── engine.py         # Vector+Graph+Lessons
├── config.yaml
├── .env
├── pyproject.toml
└── jarvis_auto_patcher.py   # Otomatik hata düzeltme
```

---

## 🔄 Güncelleme Geçmişi

| Tarih | Değişiklik |
|-------|-----------|
| 11.04.2026 | v2 Multi-Agent sistemi entegre edildi |
| 11.04.2026 | OpenRouter ücretsiz modeller desteği eklendi |
| 11.04.2026 | Coder Agent self-healing loop eklendi |
| 11.04.2026 | GUI + v2 orchestrator bağlandı |
| 11.04.2026 | qwen3.5:27b → qwen2.5:14b (12GB VRAM uyumlu) |
| 11.04.2026 | Hermes TAO loop entegrasyonu |
| 11.04.2026 | jarvis_auto_patcher.py eklendi |
