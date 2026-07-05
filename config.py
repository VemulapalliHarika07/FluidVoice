"""
Configuration management for FluidVoiceWin.
Settings are stored as JSON in %APPDATA%\\FluidVoiceWin\\config.json
"""
import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "hotkey": "ctrl+alt+space",       # global hotkey to toggle recording
    "mode": "toggle",                  # "toggle" or "push_to_talk"
    "model_size": "base",              # tiny, base, small, medium, large-v3
    "language": None,                  # None = auto-detect, or "en", "hi", "te", etc.
    "device": "cpu",                   # "cpu" or "cuda" (if you have an NVIDIA GPU + CUDA installed)
    "compute_type": "int8",            # int8 (fast, cpu-friendly) or float16 (gpu)
    "sample_rate": 16000,
    "show_overlay": True,
    "auto_add_space": True,            # append a trailing space after inserted text
    "trailing_punctuation_strip": True,
    "start_minimized": True,
    "launch_sound": False,
}


def get_config_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / "FluidVoiceWin"
    else:
        # Fallback for non-Windows / testing environments
        base = Path.home() / ".fluidvoicewin"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def load_config() -> dict:
    path = get_config_path()
    if not path.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def update_config(**kwargs) -> dict:
    cfg = load_config()
    cfg.update(kwargs)
    save_config(cfg)
    return cfg
