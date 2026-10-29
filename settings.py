"""Налаштування APEXUS 1V та шляхи до локальних даних."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from urllib.parse import urlparse

APP_NAME = "APEXUS 1V"

# Пресети: назва -> (адреса API, модель за замовчуванням). Усі мають формат OpenAI /chat/completions.
CUSTOM_PRESET = "Власний"
PRESETS: dict[str, tuple[str, str]] = {
    "DeepSeek": ("https://api.deepseek.com/chat/completions", "deepseek-chat"),
    "OpenAI": ("https://api.openai.com/v1/chat/completions", "gpt-4o-mini"),
    "OpenRouter": ("https://openrouter.ai/api/v1/chat/completions", "openai/gpt-4o-mini"),
    "Groq": ("https://api.groq.com/openai/v1/chat/completions", "llama-3.3-70b-versatile"),
    "Ollama (локально)": ("http://localhost:11434/v1/chat/completions", "llama3.2"),
    CUSTOM_PRESET: ("", ""),
}

DEFAULT_SYSTEM_PROMPT = (
    "Ти — APEXUS, дружній та уважний AI-помічник. "
    "Відповідай українською, чітко й по суті, якщо користувач не просить іншу мову."
)


def data_dir() -> Path:
    """Папка для історії чатів і налаштувань (на Windows — %APPDATA%\\APEXUS_AI)."""
    base = os.environ.get("APPDATA") or str(Path.home())
    path = Path(base) / "APEXUS_AI"
    path.mkdir(parents=True, exist_ok=True)
    return path


def atomic_write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def normalize_url(url: str) -> str:
    """Додає /chat/completions, якщо вказано лише базову адресу (напр. https://api.openai.com/v1)."""
    url = (url or "").strip().rstrip("/")
    if url and not url.lower().endswith("/chat/completions"):
        url += "/chat/completions"
    return url


def is_local_url(url: str) -> bool:
    host = urlparse(url or "").hostname or ""
    return host in ("localhost", "127.0.0.1", "::1")


def provider_name(url: str) -> str:
    host = (urlparse(url or "").hostname or "").lower()
    for part, name in (
        ("deepseek", "DeepSeek"),
        ("openai.com", "OpenAI"),
        ("openrouter", "OpenRouter"),
        ("groq", "Groq"),
    ):
        if part in host:
            return name
    if is_local_url(url):
        return "локальний сервер"
    return host or "сервіс"


@dataclass
class Settings:
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    api_key: str = ""  # ключ із налаштувань; якщо порожній — береться змінна DEEPSEEK_API_KEY
    font_size: int = 15
    animations: bool = True
    api_url: str = "https://api.deepseek.com/chat/completions"

    def get_api_key(self) -> str:
        return self.api_key.strip() or os.environ.get("DEEPSEEK_API_KEY", "").strip()

    def needs_key(self) -> bool:
        return not self.get_api_key() and not is_local_url(self.api_url)

    @staticmethod
    def _path() -> Path:
        return data_dir() / "settings.json"

    @classmethod
    def load(cls) -> "Settings":
        path = cls._path()
        if not path.exists():
            return cls()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            known = {f.name for f in fields(cls)}
            return cls(**{k: v for k, v in raw.items() if k in known})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self) -> None:
        try:
            atomic_write_json(self._path(), asdict(self))
        except OSError as exc:
            print(f"[APEXUS 1V] Не вдалося зберегти налаштування: {exc}")
