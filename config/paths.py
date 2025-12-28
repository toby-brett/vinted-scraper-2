import os
from pathlib import Path

def state_dir() -> Path:
    # Base directory for data/ids/logs per IP user
    return Path(os.environ.get("VINTED_STATE_DIR", str(Path.home() / ".local/state/vinted"))).expanduser().resolve()

def models_dir() -> Path:
    # Where models live (can be shared or per-IP)
    base = os.environ.get("VINTED_MODELS_DIR")
    if base:
        return Path(base).expanduser().resolve()
    return (state_dir() / "models").resolve()

def ensure_runtime_dirs() -> None:
    sd = state_dir()
    for sub in ("data", "ids", "logs"):
        (sd / sub).mkdir(parents=True, exist_ok=True)
    models_dir().mkdir(parents=True, exist_ok=True)

def resolve_under_state(p: str) -> str:
    """Absolute paths pass through, relative paths are placed under VINTED_STATE_DIR"""
    pp = Path(p).expanduser()
    if pp.is_absolute():
        return str(pp)
    return str((state_dir() / pp).resolve())

def resolve_under_models(p: str) -> str:
    """Absolute paths pass through; relative paths are placed under VINTED_MODELS_DIR."""
    pp = Path(p).expanduser()
    if pp.is_absolute():
        return str(pp)
    return str((models_dir() / pp).resolve())