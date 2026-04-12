"""
Jarvis Action: computer_settings — Ses, parlaklık, pencere yönetimi, WiFi, kapatma.
"""

import platform
import subprocess


def _windows_command(cmd: str) -> bool:
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception:
        return False


def run(parameters: dict, **kwargs) -> str: # type: ignore
    """Bilgisayar ayarlarını kontrol eder."""
    params = parameters or {} # type: ignore
    action = params.get("action", "").lower() # type: ignore
    description = params.get("description", "").lower() # type: ignore
    value = params.get("value", "") # type: ignore

    system = platform.system()

    if system != "Windows":
        return f"Bu eylem şu an sadece Windows'ta destekleniyor."

    # Ses kontrolü
    if any(k in description for k in ["ses", "volume", "ses seviyesi"]):
        if "aç" in description or "artır" in description or "up" in description:
            for _ in range(5):
                _windows_command("nircmd changesysvolume 6553")
            return "Ses artırıldı."
        elif "kıs" in description or "azalt" in description or "down" in description:
            for _ in range(5):
                _windows_command("nircmd changesysvolume -6553")
            return "Ses kısıldı."
        elif value:
            return f"Ses ayarı: {value} (manuel olarak ayarlamanız gerekebilir)"

    # Parlaklık
    if any(k in description for k in ["parlaklık", "brightness"]):
        return "Parlaklık ayarı Windows'ta manuel olarak yapılmalıdır."

    # WiFi
    if "wifi" in description or "kablosuz" in description:
        if any(k in description for k in ["kapat", "devre dışı", "off"]):
            _windows_command("netsh interface set interface Wi-Fi disable")
            return "WiFi kapatıldı."
        elif any(k in description for k in ["aç", "etkinleştir", "on"]):
            _windows_command("netsh interface set interface Wi-Fi enable")
            return "WiFi açıldı."

    # Kapatma / Yeniden başlatma
    if any(k in description for k in ["kapat", "shutdown", "kapat"]):
        if value == "now" or "hemen" in description:
            _windows_command("shutdown /s /f /t 0")
            return "Bilgisayar kapatılıyor."
        elif value:
            try:
                secs = int(value) # type: ignore
                _windows_command(f"shutdown /s /f /t {secs}")
                return f"Bilgisayar {secs} saniye içinde kapanacak."
            except ValueError:
                pass

    if any(k in description for k in ["yeniden başlat", "restart", "reboot"]):
        _windows_command("shutdown /r /f /t 0")
        return "Bilgisayar yeniden başlatılıyor."

    # İptal
    if any(k in description for k in ["iptal", "cancel"]):
        _windows_command("shutdown /a")
        return "Zamanlanmış kapatma iptal edildi."

    # Pencere yönetimi
    if any(k in description for k in ["pencere", "window", "ekran"]):
        if any(k in description for k in ["küçült", "minimize"]):
            _windows_command("powershell -Command \"(New-Object -ComObject WScript.Shell).SendKeys('% n')\"")
            return "Pencereler küçültüldü."
        if any(k in description for k in ["kilitle", "lock"]):
            _windows_command("rundll32.exe user32.dll,LockWorkStation")
            return "Ekran kilitleniyor."

    return f"'{description}' eylemi anlaşılamadı. Daha açık bir şekilde belirtin."
