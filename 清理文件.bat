@echo off
chcp 65001 >nul

echo ==========================================
echo       正在执行目录清理与备份还原...
echo ==========================================

cd /d "%~dp0"

echo 1. 正在删除旧文件夹...
if exist "0pre"   rd /s /q "0pre"
if exist "1audio" rd /s /q "1audio"
if exist "2vad"   rd /s /q "2vad"
if exist "3asr"   rd /s /q "3asr"

echo 2. 正在从 backup 精准还原 4 个文件夹...
:: 检查 backup 文件夹是否存在
if exist "backup" (
    
    :: 明确指定将 backup 里的每一个子文件夹，复制到当前目录下对应的同名文件夹
    if exist "backup\0pre"   xcopy "backup\0pre"   "0pre\"   /e /i /y /q
    if exist "backup\1audio" xcopy "backup\1audio" "1audio\" /e /i /y /q
    if exist "backup\2vad"   xcopy "backup\2vad"   "2vad\"   /e /i /y /q
    if exist "backup\3asr"   xcopy "backup\3asr"   "3asr\"   /e /i /y /q

    echo 还原完成！
) else (
    echo 【错误】未找到 backup 文件夹，无法复制还原！
)

echo ==========================================
echo       操作完成！
echo ==========================================
pause