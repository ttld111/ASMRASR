@echo off
:: 1. 切换到当前脚本所在的目录（确保相对路径正确）
cd /d "%~dp0"

:: 2. 激活 venv 虚拟环境
call "venv\Scripts\activate.bat"

:: 3. 启动你的 PowerShell 代码
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

:: 4. 退出虚拟环境（可选，如果你希望保持窗口打开可以注释掉）
call deactivate

pause