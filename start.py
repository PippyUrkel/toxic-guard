#!/usr/bin/env python3
"""
=========================================================================================
ToxiGuard Unified One-Command Launcher (uv Environment)
Course: Natural Language Processing (25PEC4CS1) — Fr. CRCE
=========================================================================================
Usage:
    uv run start.py
    OR
    uv run toxiguard

What this single command does automatically:
1. Starts the Flask API & 6-Module NLP Workbench on http://127.0.0.1:5000
2. Checks if frontend/react/node_modules exists (runs `npm install` automatically if missing)
3. Starts the React + Vite Frontend on http://localhost:5173
4. Prints Chrome Extension instructions and opens the dashboards in your browser
5. Gracefully terminates all background processes on Ctrl+C
"""

import os
import sys
import time
import signal
import shutil
import subprocess
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FLASK_DIR = ROOT_DIR / "toxicity_app"
REACT_DIR = ROOT_DIR / "frontend" / "react"
EXT_DIR = ROOT_DIR / "toxiguard-extension"


def print_banner():
    print("\n" + "=" * 82)
    print("🛡️  TOXIGUARD — 25PEC4CS1 NATURAL LANGUAGE PROCESSING UNIFIED LAUNCHER (uv)")
    print("🏫  Fr. Conceicao Rodrigues College of Engineering (CRCE), Mumbai")
    print("=" * 82)


def main():
    print_banner()
    processes = []

    try:
        # 1. Start Flask Backend + 6-Module NLP Workbench
        print("\n🚀 [1/3] Starting Flask NLP API & 6-Module Workbench on http://127.0.0.1:5000 ...")
        flask_env = os.environ.copy()
        flask_env["PYTHONUNBUFFERED"] = "1"
        flask_proc = subprocess.Popen(
            [sys.executable, str(FLASK_DIR / "app.py")],
            cwd=str(FLASK_DIR),
            env=flask_env,
        )
        processes.append(("Flask NLP Server", flask_proc))

        # 2. Check & Start React Frontend (if npm is installed)
        npm_cmd = shutil.which("npm")
        if npm_cmd and REACT_DIR.exists():
            node_modules = REACT_DIR / "node_modules"
            if not node_modules.exists():
                print("📦 [2/3] Installing React frontend dependencies (first-time setup via npm install)...")
                subprocess.run([npm_cmd, "install"], cwd=str(REACT_DIR), check=False)

            print("⚡ [2/3] Starting React + Vite Frontend on http://localhost:5173 ...")
            react_proc = subprocess.Popen(
                [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
                cwd=str(REACT_DIR),
            )
            processes.append(("React Vite Server", react_proc))
        else:
            print("⚠️  [2/3] Node.js / npm not detected on PATH — skipping React dev server.")
            print("    (The full 6-Module NLP Workbench UI is still live at http://127.0.0.1:5000)")

        # 3. Display Chrome Extension & Unified URLs
        time.sleep(2.0)
        print("\n" + "-" * 82)
        print("✅ ALL TOXIGUARD SERVICES ARE LIVE!")
        print("-" * 82)
        print("🔹 Flask 6-Module NLP Workbench : http://127.0.0.1:5000")
        print("🔹 Flask REST API Endpoint      : POST http://127.0.0.1:5000/predict")
        if npm_cmd:
            print("🔹 React Landing Page & UI      : http://localhost:5173")
        print(f"🔹 WhatsApp Chrome Extension    : Load unpacked -> {EXT_DIR}")
        print("-" * 82)
        print("💡 Press Ctrl+C at any time to stop all services cleanly.\n")

        # Open browser tabs automatically (unless --no-browser is passed)
        if "--no-browser" not in sys.argv:
            try:
                webbrowser.open("http://127.0.0.1:5000")
                if npm_cmd:
                    webbrowser.open("http://localhost:5173")
            except Exception:
                pass

        # Monitor child processes
        while True:
            time.sleep(1.0)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  {name} exited with code {proc.returncode}. Shutting down remaining services...")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n🛑 Stopping all ToxiGuard services...")
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=4)
                except Exception:
                    proc.kill()
        print("✅ All ToxiGuard services stopped cleanly.")


if __name__ == "__main__":
    main()
