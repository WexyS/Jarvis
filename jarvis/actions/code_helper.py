"""
Jarvis Action: code_helper — Kod yazma, düzenleme, açıklama, çalıştırma.
Ollama kullanır, Gemini gerektirmez.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("JARVIS_MODEL", "qwen2.5:14b")


def _ollama_chat(messages: list[dict], max_tokens: int = 2048) -> str: # type: ignore
    """Ollama'ya mesaj gönderir ve yanıt döner."""
    try:
        import requests
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": max_tokens}
            }, # type: ignore
            timeout=120,
        )
        result = response.json()
        return result.get("message", {}).get("content", "")
    except Exception as e:
        return f"Ollama hatası: {e}"


def _clean_code(text: str) -> str:
    """Markdown kod bloklarını temizler."""
    text = text.strip()
    # ```language\ncode\n``` kalıbını çıkar
    match = re.search(r"```[a-zA-Z]*\n([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


def _resolve_save_path(output_path: str, language: str) -> Path:
    ext_map = {
        "python": ".py", "py": ".py",
        "javascript": ".js", "js": ".js",
        "typescript": ".ts", "ts": ".ts",
        "html": ".html", "css": ".css",
        "java": ".java", "cpp": ".cpp", "c": ".c",
        "bash": ".sh", "powershell": ".ps1",
        "sql": ".sql", "json": ".json", "rust": ".rs", "go": ".go",
    }
    if output_path:
        p = Path(output_path)
        return p if p.is_absolute() else Path.cwd() / p
    ext = ext_map.get((language or "python").lower(), ".py")
    return Path.cwd() / f"jarvis_output{ext}"


def _read_file(file_path: str) -> tuple: # type: ignore
    if not file_path:
        return "", "Dosya yolu belirtilmedi."
    p = Path(file_path)
    if not p.exists():
        return "", f"Dosya bulunamadı: {file_path}"
    try:
        return p.read_text(encoding="utf-8", errors="replace"), ""
    except Exception as e:
        return "", f"Dosya okunamadı: {e}"


def _save_file(path: Path, content: str) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Kaydedildi: {path}"
    except Exception as e:
        return f"Kaydetme hatası: {e}"


def run(parameters: dict, **kwargs) -> str: # type: ignore
    """Kod ile ilgili işlemler yapar."""
    p = parameters or {} # type: ignore
    action = p.get("action", "auto").lower().strip() # type: ignore
    description = p.get("description", "").strip() # type: ignore
    language = p.get("language", "python").strip() # type: ignore
    output_path = p.get("output_path", "").strip() # type: ignore
    file_path = p.get("file_path", "").strip() # type: ignore
    code = p.get("code", "").strip() # type: ignore
    timeout = int(p.get("timeout", 30)) # type: ignore

    # Otomatik intent tespiti
    if action == "auto":
        desc_lower = description.lower() # type: ignore
        if file_path:
            p_obj = Path(file_path) # type: ignore
            if p_obj.exists() and any(k in desc_lower for k in ["açıkla", "explain", "ne yapıyor", "what does"]):
                action = "explain"
            elif p_obj.exists() and any(k in desc_lower for k in ["düzenle", "değiştir", "edit", "change", "ekle"]):
                action = "edit"
            elif p_obj.exists() and any(k in desc_lower for k in ["çalıştır", "run", "execute"]):
                action = "run"
            elif p_obj.exists():
                action = "explain"
        elif code:
            if any(k in desc_lower for k in ["açıkla", "explain"]):
                action = "explain"
            else:
                action = "edit"
        else:
            action = "write"

    # ── Yazma ──
    if action == "write":
        if not description:
            return "Ne yazmamı istediğinizi açıklayın."
        messages = [
            {"role": "system", "content": f"Sen uzman bir {language} geliştiricisisin. Sadece kodu yaz, açıklama yapma. Markdown kullanma."},
            {"role": "user", "content": f"{language} kodu yaz:\n\n{description}"}
        ]
        code_result = _ollama_chat(messages)
        clean = _clean_code(code_result)
        save_path = _resolve_save_path(output_path, language) # type: ignore
        status = _save_file(save_path, clean)
        return f"Kod yazıldı.\n{status}\n\nÖnizleme:\n{clean[:500]}"

    # ── Düzenleme ──
    elif action == "edit":
        if not file_path:
            return "Düzenlenecek dosya yolunu belirtin."
        content, err = _read_file(file_path) # type: ignore
        if err:
            return err # type: ignore
        messages = [
            {"role": "system", "content": "Sen uzman bir kod editörüsün. Aşağıdaki değişiklikleri koda uygula. SADECE tam güncellenmiş kodu döner, başka bir şey yazma."},
            {"role": "user", "content": f"Değişiklik: {description}\n\nOrijinal kod:\n{content}"}
        ]
        result = _ollama_chat(messages)
        clean = _clean_code(result)
        status = _save_file(Path(file_path), clean) # type: ignore
        return f"Dosya düzenlendi. {status}\n\nÖnizleme:\n{clean[:500]}"

    # ── Açıklama ──
    elif action == "explain":
        if file_path and not code:
            code, err = _read_file(file_path) # type: ignore
            if err:
                return err # type: ignore
        if not code:
            return "Açıklanacak kodu veya dosya yolunu belirtin."
        messages = [
            {"role": "system", "content": "Bu kodun ne yaptığını basit ve net bir dille açıkla. 3-6 cümle."},
            {"role": "user", "content": f"Kod:\n{code[:4000]}"}
        ]
        return _ollama_chat(messages)

    # ── Çalıştırma ──
    elif action == "run":
        if not file_path:
            return "Çalıştırılacak dosya yolunu belirtin."
        p_obj = Path(file_path) # type: ignore
        if not p_obj.exists():
            return f"Dosya bulunamadı: {file_path}"
        interpreters = {
            ".py":  [sys.executable],
            ".js":  ["node"],
            ".ts":  ["npx", "ts-node"],
            ".sh":  ["bash"],
            ".ps1": ["powershell", "-File"],
            ".rb":  ["ruby"],
            ".php": ["php"],
        }
        interp = interpreters.get(p_obj.suffix.lower())
        if not interp:
            return f"{p_obj.suffix} dosyası için yorumlayıcı bulunamadı."
        try:
            result = subprocess.run(
                interp + [str(p_obj)],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout, cwd=str(p_obj.parent)
            )
            parts = []
            if result.stdout.strip():
                parts.append(f"Çıktı:\n{result.stdout.strip()}") # type: ignore
            if result.stderr.strip():
                parts.append(f"Hata:\n{result.stderr.strip()}") # type: ignore
            return "\n\n".join(parts) if parts else "Çalıştırıldı, çıktı yok." # type: ignore
        except subprocess.TimeoutExpired:
            return f"{timeout} saniye zaman aşımı."
        except Exception as e:
            return f"Çalıştırma hatası: {e}"

    else:
        return f"Bilinmeyen eylem: '{action}'. Desteklenenler: write, edit, explain, run."
