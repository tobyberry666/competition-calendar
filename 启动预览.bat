@echo off
echo ========================================
echo   大学生竞赛日历 - 本地预览服务器
echo ========================================
echo.
echo 正在启动本地服务器...
echo 启动后请在浏览器打开: http://localhost:8000
echo 按 Ctrl+C 停止服务器
echo.

cd /d "%~dp0frontend"
python -m http.server 8000

pause
