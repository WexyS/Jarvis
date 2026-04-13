# NVIDIA PersonaPlex Kurulum ve Entegrasyon

## 📦 Kurulum Tamamlandı ✅

### Yüklelenen Kütüphaneler:
- ✅ torch>=2.0.0
- ✅ torchvision
- ✅ torchaudio
- ✅ transformers>=4.35.0
- ✅ accelerate
- ✅ huggingface_hub
- ✅ sounddevice
- ✅ soundfile
- ✅ librosa

### Python Sürümü:
- ✅ Python 3.11.0 (PersonaPlex için uygun)

## ⚠️ Yapılması Gerekenler

### 1. HuggingFace Token (GEREKLİ)
```bash
# .env dosyasına ekle:
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Token almak için:
# https://huggingface.co/settings/tokens
```

### 2. NVIDIA GPU (ÖNERİLEN)
- RTX 4080 12GB ✅ Mevcut
- CUDA 12.x desteği gerekli

### 3. PersonaPlex Model İndirme (OPSİYONEL)
```bash
# Model büyük - sadece sesli konuşma özelliği istiyorsan indir
git clone https://github.com/NVIDIA/personaplex.git
cd personaplex
pip install -e .
```

## 🎯 Kullanım

### Basit Kullanım (Mevcut TTS)
```python
# Mevcut edge-tts sistemi kullanmaya devam edebilir
from ultron.tts_voice import speak
await speak("Merhaba!")
```

### PersonaPlex (Gelecekte)
```python
# PersonaPlex full-duplex sesli konuşma
from personaplex import PersonaPlexClient

client = PersonaPlexClient(
    voice="NATF0",  # Kadın sesi
    role="Professional AI assistant named Ultron"
)

# Sesli yanıt
response = await client.chat(audio_input=user_voice)
```

## 📊 Performans

| Özellik | Mevcut (edge-tts) | PersonaPlex |
|---------|-------------------|-------------|
| **Kurulum** | ✅ Basit | ⚠️ Karmaşık |
| **GPU** | Gerekmez | Önerilen |
| **Kalite** | İyi | Mükemmel |
| **Latency** | Düşük | Çok düşük |
| **Full-Duplex** | ❌ Yok | ✅ Var |
| **Persona** | ❌ Sabit | ✅ Değiştirilebilir |

## 💡 Öneri

**Şimdilik:** edge-tts kullan (basit, çalışıyor)
**Gelecekte:** PersonaPlex'e geç (daha kaliteli, full-duplex)
