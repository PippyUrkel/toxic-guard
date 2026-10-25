#!/usr/bin/env python3
"""
=========================================================================================
ToxiGuard Unified Launcher (uv Environment)
Course: Natural Language Processing (25PEC4CS1) — Fr. CRCE
=========================================================================================
Usage:
    uv run start.py
    OR
    uv run toxiguard

What this single command does automatically:
1. Starts the Flask NLP API & Unified Workbench on http://127.0.0.1:5000
2. Waits until Flask is healthy on port 5000 before opening client connections
3. Builds/starts the React frontend on http://localhost:5173
4. Optionally connects Discord Moderation Bot (if DISCORD_BOT_TOKEN is set)
5. Gracefully handles failures without crashing companion services
"""

import os
import sys
import time
import shutil
import urllib.request
import subprocess
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
FLASK_DIR = ROOT_DIR / "toxicity_app"
REACT_DIR = ROOT_DIR / "frontend" / "react"
BOT_DIR = ROOT_DIR / "discord_bot"

# Load .env file
try:
    from dotenv import load_dotenv
    if (ROOT_DIR / ".env").exists():
        load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


def print_banner():
    print("\n" + "=" * 80)
    print("TOXIGUARD — 25PEC4CS1 NATURAL LANGUAGE PROCESSING UNIFIED PLATFORM")
    print("Department of Computer Engineering • Fr. CRCE, Mumbai")
    print("=" * 80)


def wait_for_flask_ready(timeout_sec: float = 20.0) -> bool:
    """Polls Flask health endpoint until server is listening and ready."""
    print("[INFO] Waiting for Flask NLP API to initialize on http://127.0.0.1:5000...")
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/api/health", timeout=1.0) as resp:
                if resp.status == 200:
                    print("[OK] Flask NLP API is ready and listening on http://127.0.0.1:5000")
                    return True
        except Exception:
            time.sleep(0.4)
    print("[WARN] Flask health check timed out; proceeding with frontend startup.")
    return False


def main():
    print_banner()
    processes = []

    try:
        # 1. Start Flask Backend + Unified NLP Engine
        print("\n[START] [1/3] Starting Flask NLP Server on http://127.0.0.1:5000 ...")
        flask_env = os.environ.copy()
        flask_env["PYTHONUNBUFFERED"] = "1"
        flask_proc = subprocess.Popen(
            [sys.executable, str(FLASK_DIR / "app.py")],
            cwd=str(FLASK_DIR),
            env=flask_env,
        )
        processes.append(("Flask Server", flask_proc))

        # Wait for Flask to bind and become healthy to prevent [vite] ECONNREFUSED
        wait_for_flask_ready(timeout_sec=20.0)

        # 2. Check & Start React Frontend (Vite)
        npm_cmd = shutil.which("npm")
        if npm_cmd and REACT_DIR.exists():
            node_modules = REACT_DIR / "node_modules"
            if not node_modules.exists():
                print("[INFO] [2/3] Installing React frontend dependencies via npm install...")
                subprocess.run([npm_cmd, "install"], cwd=str(REACT_DIR), check=False)

            # Ensure dist/ exists for direct Flask serving
            dist_dir = REACT_DIR / "dist"
            if not dist_dir.exists():
                print("[INFO] [2/3] Building frontend assets for unified server...")
                subprocess.run([npm_cmd, "run", "build"], cwd=str(REACT_DIR), check=False)

            print("[START] [2/3] Starting React + Vite Frontend on http://localhost:5173 ...")
            react_proc = subprocess.Popen(
                [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
                cwd=str(REACT_DIR),
            )
            processes.append(("React Vite Server", react_proc))
        else:
            print("[INFO] [2/3] Node.js / npm not detected on PATH — serving unified build via Flask on port 5000.")

        # 3. Check Discord Bot Token
        discord_token = os.environ.get("DISCORD_BOT_TOKEN")
        if discord_token and discord_token.strip() != "your_discord_bot_token_here":
            print("\n[START] [3/3] DISCORD_BOT_TOKEN detected — launching Discord Moderation Bot...")
            bot_proc = subprocess.Popen(
                [sys.executable, str(BOT_DIR / "bot.py")],
                cwd=str(ROOT_DIR),
            )
            processes.append(("Discord Bot", bot_proc))
        else:
            print("\n[INFO] [3/3] Discord Bot: DISCORD_BOT_TOKEN not configured in .env.")
            print("       To run the Discord bot:")
            print("         * Real Discord Gateway : Set DISCORD_BOT_TOKEN in .env and run: uv run python discord_bot/bot.py")
            print("         * Offline Simulation  : uv run python discord_bot/bot.py --simulate")

        time.sleep(1.0)
        print("\n" + "-" * 80)
        print("[OK] TOXIGUARD SERVICES ARE LIVE")
        print("-" * 80)
        print("  * Unified Web Interface & API : http://127.0.0.1:5000")
        print("  * REST API Prediction Endpoint: POST http://127.0.0.1:5000/predict")
        if npm_cmd:
            print("  * React Hot-Reload Dev Server : http://localhost:5173")
        print("  * Discord Bot Module          : discord_bot/bot.py")
        print("-" * 80)
        print("[INFO] Press Ctrl+C at any time to stop all services.\n")

        # Open browser tab (unless --no-browser is passed)
        if "--no-browser" not in sys.argv:
            try:
                target_url = "http://localhost:5173" if npm_cmd else "http://127.0.0.1:5000"
                webbrowser.open(target_url)
            except Exception:
                pass

        # Monitor child processes with resilient fault tolerance
        active_processes = list(processes)
        while True:
            time.sleep(1.0)
            for item in list(active_processes):
                name, proc = item
                if proc.poll() is not None:
                    if name == "Flask Server":
                        print(f"[ERROR] Core Flask API Server stopped (code {proc.returncode}). Shutting down all services...")
                        raise KeyboardInterrupt
                    elif name == "Discord Bot":
                        print(f"[WARN] Discord Bot process exited (code {proc.returncode}). The unified web interface and API remain live.")
                        active_processes.remove(item)
                    elif name == "React Vite Server":
                        print(f"[WARN] React Vite dev server stopped (code {proc.returncode}). Serving via Flask.")
                        active_processes.remove(item)

    except KeyboardInterrupt:
        print("\n[STOP] Stopping all ToxiGuard services...")
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=4)
                except Exception:
                    proc.kill()
        print("[OK] All ToxiGuard services stopped cleanly.")


if __name__ == "__main__":
    main()
