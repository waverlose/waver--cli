@echo off
chcp 65001 >nul
cd /d "%~dp0src"
pip show waver >nul 2>&1
if %errorlevel% neq 0 (
    echo 首次安装...
    pip install -e .
) else (
    echo 直接运行
)
python -m waver
pause
