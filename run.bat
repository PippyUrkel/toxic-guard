@echo off
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
)
uv run start.py %*
