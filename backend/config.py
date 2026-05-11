import os
from pathlib import Path
from dotenv import load_dotenv


def load_env():
    project_root = Path(__file__).resolve().parents[1]
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"[ENV] Loaded: {env_path}")
    else:
        print(f"[ENV] Missing: {env_path}")

    return env_path