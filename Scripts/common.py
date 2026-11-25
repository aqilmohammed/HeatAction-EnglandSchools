from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def config():
    cfg = json.loads((ROOT / "Config" / "project_config.json").read_text(encoding="utf-8"))
    return cfg

def path(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT / p

def outdir(*parts):
    p = ROOT / "Outputs"
    for part in parts:
        p = p / part
    p.mkdir(parents=True, exist_ok=True)
    return p
