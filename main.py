"""
Main pipeline runner — runs the full data pipeline in order:
1. Test Snowflake connection
2. Run EDA (saves charts to outputs/)
3. Train ML model (saves model to models/)

Usage:
    python main.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Support both the original src/ layout and the flat layout supplied with this project.
def script_path(name):
    nested = ROOT / "src" / name
    flat = ROOT / name
    return nested if nested.exists() else flat

STEPS = [
    ("Connecting to Snowflake & verifying data", script_path("connect_snowflake.py")),
    ("Running EDA", script_path("eda.py")),
    ("Training ML model", script_path("train_model.py")),
]

def run_step(title, script_path):
    print("\n" + "=" * 60)
    print(f"STEP: {title}")
    print("=" * 60)
    if title == "Running EDA":
        (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    if title == "Training ML model":
        (ROOT / "models").mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, str(script_path)], cwd=ROOT)
    if result.returncode != 0:
        print(f"\n❌ Failed at: {title} (exit code {result.returncode})")
        sys.exit(1)
    print(f"✅ Done: {title}")

if __name__ == "__main__":
    for title, script in STEPS:
        run_step(title, script)
    print("\n🎉 Pipeline complete — model trained, charts saved, ready for app.py")