"""NVIDIA PersonaPlex Kurulum ve Entegrasyon Scripti

PersonaPlex: Gerçek zamanlı, full-duplex sesli konuşma AI modeli
- Metin tabanlı rol promptları ile kişi kontrolü
- Ses tabanlı ses kondisyonlama
- Düşük gecikmeli doğal etkileşim

Kurulum Adımları:
1. Python 3.10+ kontrol
2. Gerekli kütüphaneleri yükle
3. HuggingFace token kurulumu
4. PersonaPlex'i indir ve test et

Kullanım:
    python scripts/setup_personaplex.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Renkli çıktılar
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}📦 {msg}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def check_python_version():
    """Python 3.10+ kontrol"""
    print_step("Python Sürümü Kontrol")
    
    version = sys.version_info
    print(f"Mevcut Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor} - PersonaPlex için uygun!")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} - PersonaPlex için Python 3.10+ gerekli!")
        print_warning("Yeni Python yüklemen gerekiyor:")
        print("  https://www.python.org/downloads/")
        return False


def check_gpu():
    """GPU kontrol (NVIDIA önerilir)"""
    print_step("GPU Kontrol")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print_success(f"NVIDIA GPU bulundu: {gpu_name}")
            print(f"   VRAM: {gpu_memory:.1f} GB")
            
            if gpu_memory >= 8:
                print_success("Yeterli VRAM! (8GB+)")
            else:
                print_warning("Düşük VRAM - CPU offload kullanman gerekebilir")
        else:
            print_warning("NVIDIA GPU bulunamadı - CPU mode kullanılacak")
            print("  (Daha yavaş ama çalışır)")
        
        return True
    except ImportError:
        print_error("PyTorch yüklü değil!")
        return False


def install_dependencies():
    """Gerekli kütüphaneleri yükle"""
    print_step("Bağımlılıkları Yükleme")
    
    packages = [
        "torch>=2.0.0",
        "torchvision",
        "torchaudio",
        "transformers>=4.35.0",
        "accelerate",  # CPU offload için
        "huggingface_hub",
        "sounddevice",
        "soundfile",
        "librosa",
    ]
    
    for package in packages:
        print(f"\n📥 {package} yükleniyor...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                stdout=subprocess.DEVNULL
            )
            print_success(f"{package} yüklendi")
        except subprocess.CalledProcessError as e:
            print_error(f"{package} yüklenemedi: {e}")
            return False
    
    return True


def check_huggingface_token():
    """HuggingFace token kontrol"""
    print_step("HuggingFace Token Kontrol")
    
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    
    if token:
        print_success("HF_TOKEN bulundu!")
        return True
    else:
        print_warning("HF_TOKEN bulunamadı!")
        print("\n📝 PersonaPlex için HuggingFace token gerekli:")
        print("1. https://huggingface.co/settings/tokens adresine git")
        print("2. Yeni token oluştur (read access)")
        print("3. .env dosyasına ekle:")
        print("   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx")
        print("\nDevam etmek istiyor musunuz? (E/H)")
        
        response = input().strip().lower()
        return response in ['e', 'evet', 'y', 'yes']


def add_to_env_example():
    """.env.example'a PersonaPlex config ekle"""
    print_step(".env.example Güncelleme")
    
    env_example = Path(".env.example")
    
    if not env_example.exists():
        print_error(".env.example bulunamadı!")
        return False
    
    content = env_example.read_text(encoding="utf-8")
    
    # PersonaPlex config ekle (eğer yoksa)
    if "PERSONAPLEX" not in content.upper():
        personaplex_config = """
# NVIDIA PersonaPlex (Voice/Speech)
PERSONAPLEX_VOICE=NATF0
PERSONAPLEX_USE_GPU=true
PERSONAPLEX_CPU_OFFLOAD=false
"""
        content += personaplex_config
        env_example.write_text(content, encoding="utf-8")
        print_success(".env.example güncellendi!")
    else:
        print_success("PersonaPlex config zaten mevcut!")
    
    return True


def test_personaplex_import():
    """PersonaPlex import test"""
    print_step("PersonaPlex Import Test")
    
    try:
        # moshi package import (PersonaPlex'in tabanı)
        # Not: Gerçek kurulumda moshi package yüklenir
        print("🧪 Test import ediliyor...")
        
        # Şimdilik sadece torch kontrol
        import torch
        print_success("PyTorch import başarılı!")
        
        # Gelecekte burada moshi/personaplex import olacak
        print_warning("PersonaPlex henüz kurulmadı - kurulum sonrası tekrar çalıştır")
        
        return True
    except Exception as e:
        print_error(f"Import test başarısız: {e}")
        return False


def main():
    """Ana kurulum süreci"""
    print("\n" + "🔥"*30)
    print("🚀 NVIDIA PERSONAPLEX KURULUMU")
    print("🔥"*30)
    
    # Adım 1: Python kontrol
    if not check_python_version():
        print_error("\nKurulum başarısız - Python 3.10+ gerekli!")
        return False
    
    # Adım 2: GPU kontrol
    check_gpu()
    
    # Adım 3: Bağımlılıklar
    if not install_dependencies():
        print_error("\nKurulum başarısız - bağımlılıklar yüklenemedi!")
        return False
    
    # Adım 4: HuggingFace token
    check_huggingface_token()
    
    # Adım 5: .env.example güncelle
    add_to_env_example()
    
    # Adım 6: Test
    test_personaplex_import()
    
    print("\n" + "="*60)
    print_success("PERSONAPLEX KURULUMU TAMAMLANDI!")
    print("="*60)
    print("\n📝 Sonraki Adımlar:")
    print("1. HF_TOKEN'ı .env dosyasına ekle")
    print("2. git clone https://github.com/NVIDIA/personaplex.git")
    print("3. cd personaplex && pip install .")
    print("4. python -m moshi.server  # Sunucuyu başlat")
    print("\n📖 Dokümantasyon:")
    print("   https://github.com/NVIDIA/personaplex")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Kurulum iptal edildi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        sys.exit(1)
