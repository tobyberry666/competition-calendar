@echo off
chcp 65001 >nul
echo ========================================
echo   大学生竞赛日历 - 一键部署到 GitHub
echo ========================================
echo.

cd /d "%~dp0"

REM 检查是否已经初始化过
if exist .git (
    echo Git 仓库已存在，跳过初始化
) else (
    echo 正在初始化 Git 仓库...
    git init
    git add .
    git commit -m "init: 大学生竞赛日历项目"
)

echo.
echo ========================================
echo  请输入你的 GitHub Token (ghp_开头的那串)
echo  获取地址: https://github.com/settings/tokens/new
echo  记得勾选 repo 权限！
echo ========================================
set /p TOKEN=Token: 

if "%TOKEN%"=="" (
    echo 错误：Token 不能为空
    pause
    exit /b
)

echo.
echo 正在推送到 GitHub...
git branch -M main

REM 检查是否已有 remote
git remote get-url origin >nul 2>&1
if %errorlevel%==0 (
    git remote set-url origin https://%TOKEN%@github.com/tobyberry666/competition-calendar.git
) else (
    git remote add origin https://%TOKEN%@github.com/tobyberry666/competition-calendar.git
)

git push -u origin main

if %errorlevel%==0 (
    echo.
    echo ✅ 推送成功！
    echo.
    echo 接下来请手动操作：
    echo 1. 打开仓库: https://github.com/tobyberry666/competition-calendar
    echo 2. Settings -^> Pages -^> Source 选 GitHub Actions
    echo 3. Actions -^> 每日竞赛数据更新 -^> Run workflow
    echo 4. 等2分钟后访问: https://tobyberry666.github.io/competition-calendar/
) else (
    echo.
    echo ❌ 推送失败！
    echo 请检查：
    echo - Token 是否正确（要有repo权限）
    echo - 仓库是否已创建: https://github.com/new
    echo - 仓库名是否是 competition-calendar
)

echo.
pause
