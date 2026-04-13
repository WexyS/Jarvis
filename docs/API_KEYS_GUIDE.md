# 🔑 API Keys - Nereden Alınır ve Nasıl Kullanılır?

## 📋 İçindekiler

1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [AI Provider API Keys](#ai-provider-api-keys)
3. [HuggingFace Token](#huggingface-token)
4. [Diğer API Keys](#diğer-api-keys)
5. [Güvenlik Notları](#güvenlik-notları)

---

## 🚀 Hızlı Başlangıç

### 1. `.env` Dosyası Oluştur

```bash
# Proje kök dizininde:
copy .env.example .env
```

### 2. API Key'leri Ekle

```env
# .env dosyası:
OPENROUTER_API_KEY=sk-or-v1-...
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
# ... diğer keys
```

---

## 🤖 AI Provider API Keys

### 1. OpenRouter (ÖNERİLEN - 200+ model)

**Nereden Alınır:**
1. https://openrouter.ai/ adresine git
2. Sign Up (Google/GitHub ile)
3. Credits → Add Credit (minimum $5)
4. API Keys → Create Key

**.env'e Ekle:**
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
```

**Kullanım:**
- 200+ model (GPT-4, Claude, Gemini, Llama, vb.)
- Pay-as-you-go (kullandığın kadar öde)
- Free tier modeller de var!

---

### 2. Groq (ÜCRETSİZ - Hızlı!)

**Nereden Alınır:**
1. https://console.groq.com/ adresine git
2. Sign Up (GitHub ile)
3. API Keys → Create API Key

**.env'e Ekle:**
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

**Kullanım:**
- ✅ ÜCRETSİZ (şu anda)
- 🚀 Çok hızlı (500+ tok/s)
- Llama 3.1 8B/70B, Mixtral, Gemma

---

### 3. Google Gemini (ÜCRETSİZ - 1M context)

**Nereden Alınır:**
1. https://aistudio.google.com/ adresine git
2. Sign In (Google hesabınla)
3. Get API Key

**.env'e Ekle:**
```env
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxx
```

**Kullanım:**
- ✅ ÜCRETSİZ (15 RPM limit)
- 📝 1M token context window!
- Gemini 2.0 Flash/Pro

---

### 4. Anthropic Claude (ÜCRETLİ - En iyi kalite)

**Nereden Alınır:**
1. https://console.anthropic.com/ adresine git
2. Sign Up
3. API Keys → Create Key

**.env'e Ekle:**
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxx
```

**Kullanım:**
- 💳 ÜCRETLİ ($15-20/M token)
- 🏆 En iyi kalite (Claude 3.5/4)
- Kod yazma, analiz için mükemmel

---

### 5. OpenAI (ÜCRETLİ - GPT-4)

**Nereden Alınır:**
1. https://platform.openai.com/ adresine git
2. Sign Up
3. API Keys → Create new secret key

**.env'e Ekle:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

**Kullanım:**
- 💳 ÜCRETLİ ($2.50-10/M token)
- GPT-4o, GPT-4 Turbo, o1, o3
- $5-10 başlangıç kredisi veriyor

---

## 🤗 HuggingFace Token

### Nereden Alınır?

1. https://huggingface.co/settings/tokens adresine git
2. Sign Up (e-posta ile)
3. Create New Token
4. Name: `ultron-access`
5. Role: **Read** (sadece okuma)
6. Copy token

### Kullanım Alanları:

**1. AirLLM 405B Model İndirme:**
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

**2. PersonaPlex Voice:**
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

**3. LlamaFactory Fine-tuning:**
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

### Önemli Notlar:

- ⚠️ Token'ı **KİMSEYLE PAYLAŞMA!**
- ✅ Sadece **READ** permission yeterli
- ✅ ÜCRETSİZ
- ✅ Models download için gerekli

---

## 🎯 Diğer API Keys

### Cloudflare Workers AI

**Nereden:**
1. https://dash.cloudflare.com/
2. Workers & Pages → Create
3. API Tokens → Create Token

```env
CLOUDFLARE_API_KEY=cfut_xxxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxx
```

**Özellik:**
- ✅ ÜCRETSİZ (10K/day)
- Llama, Mistral, Gemma modelleri

---

### Together AI

**Nereden:**
1. https://api.together.ai/
2. Sign Up
3. API Keys → Create

```env
TOGETHER_API_KEY=tgp_v1_xxxxxxxxxxxxxxxxxxxxx
```

**Özellik:**
- ✅ ÜCRETSİZ ($25 başlangıç kredisi)
- Llama, Qwen, Mistral modelleri

---

### HuggingFace Inference API

**Nereden:**
- Aynı HF_TOKEN kullanılır!

```env
HF_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx  # HF_TOKEN ile aynı
```

**Özellik:**
- ✅ ÜCRETSİZ (rate limited)
- 100K+ model erişim

---

### Fireworks AI

**Nereden:**
1. https://fireworks.ai/
2. Sign Up
3. API Keys → Create

```env
FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxxxxxxx
```

**Özellik:**
- ✅ ÜCRETSİZ (sınırlı)
- Llama, Mixtral, Qwen

---

### Mistral AI

**Nereden:**
1. https://console.mistral.ai/
2. Sign Up
3. API Keys → Create

```env
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

**Özellik:**
- ✅ ÜCRETSİZ (sınırlı)
- Mistral Large, Medium, Small

---

### Cohere

**Nereden:**
1. https://dashboard.cohere.com/
2. Sign Up
3. API Keys → Create

```env
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

**Özellik:**
- ✅ ÜCRETSİZ (100 calls)
- Rerank, Embed, Generate

---

## 📋 TAM `.env` DOSYASI ÖRNEĞİ

```env
# ═══════════════════════════════════════════
# ULTRON v2.1 - API Keys Configuration
# ═══════════════════════════════════════════

# ── AI Providers ──────────────────────────
# OpenRouter (200+ models - ÖNERİLEN)
OPENROUTER_API_KEY=sk-or-v1-...

# Groq (Hızlı - Ücretsiz)
GROQ_API_KEY=gsk_...

# Google Gemini (1M context - Ücretsiz)
GEMINI_API_KEY=AIzaSyD...

# Anthropic Claude (En iyi kalite)
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI GPT-4
OPENAI_API_KEY=sk-proj-...

# Cloudflare Workers AI (Ücretsiz 10K/day)
CLOUDFLARE_API_KEY=cfut_...
CLOUDFLARE_ACCOUNT_ID=...

# Together AI ($25 free credit)
TOGETHER_API_KEY=tgp_v1_...

# HuggingFace (Inference API)
HF_API_KEY=hf_...

# Fireworks AI
FIREWORKS_API_KEY=fw_...

# Mistral AI
MISTRAL_API_KEY=...

# Cohere
COHERE_API_KEY=...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# ── HuggingFace (Model Download) ──────────
# AirLLM 405B, PersonaPlex, LlamaFactory için GEREKLİ
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# ── AirLLM (Llama 3.1 405B) ──────────────
AIRLLM_MODEL=meta-llama/Llama-3.1-405B-Instruct
AIRLLM_COMPRESSION=4bit
AIRLLM_PREFETCHING=true

# ── Ollama (Local LLM) ───────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b

# ── Email (Optional) ─────────────────────
ULTRON_EMAIL_USER=your@email.com
ULTRON_EMAIL_PASS=your_app_password

# ── Language ─────────────────────────────
ULTRON_LANGUAGE=tr
```

---

## 🔒 Güvenlik Notları

### ✅ DO (Yap)

- ✅ `.env` dosyasını `.gitignore`'a ekle
- ✅ API key'leri environment variable olarak sakla
- ✅ Read-only tokens kullan (mümkünse)
- ✅ Key rotation yap (her 3-6 ayda)

### ❌ DON'T (Yapma)

- ❌ `.env` dosyasını GitHub'a push ETME!
- ❌ API key'leri kod içinde hardcode ETME!
- ❌ Key'leri Discord/Slack'te PAYLAŞMA!
- ❌ Admin/Write permission verme (sadece gerekliyse)

---

## 🆓 ÜCRETSİZ Başlangıç Paketi

**Minimum gereksinimler:**

```env
# 1. OpenRouter (200+ model - $5 credit)
OPENROUTER_API_KEY=sk-or-v1-...

# 2. HuggingFace (Model download - FREE)
HF_TOKEN=hf_...

# 3. Ollama (Local - FREE)
# Ollama kur: https://ollama.ai
# Model indir: ollama pull qwen2.5:14b
```

**Bu kadar! Gerisi opsiyonel.**

---

## 💰 Maliyet Tablosu

| Provider | Fiyat | Free Tier |
|----------|-------|-----------|
| **OpenRouter** | $5-20/M token | ❌ Yok (ama 200+ model) |
| **Groq** | Ücretsiz | ✅ Evet |
| **Gemini** | Ücretsiz | ✅ 15 RPM |
| **Cloudflare** | Ücretsiz | ✅ 10K/day |
| **Together** | $0.20/M token | ✅ $25 credit |
| **OpenAI** | $2.50-10/M token | ✅ $5-10 credit |
| **Anthropic** | $15-20/M token | ❌ Yok |
| **HuggingFace** | Ücretsiz | ✅ Rate limited |

---

## 📖 Daha Fazla Bilgi

- [OpenRouter Docs](https://openrouter.ai/docs)
- [HuggingFace Tokens](https://huggingface.co/settings/tokens)
- [Groq Console](https://console.groq.com/)
- [Gemini Studio](https://aistudio.google.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [OpenAI Platform](https://platform.openai.com/)

---

<div align="center">

**Sorun mu var? Discord/Slack'te sor!**

</div>
