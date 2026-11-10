@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" ativar_ia.py
) else (
  py -3.12 ativar_ia.py
)
