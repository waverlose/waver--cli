@echo off
echo ========================================
echo   Waver CLI 发布脚本
echo ========================================
echo.

REM 拉取最新
git pull

REM 添加所有修改
git add .

REM 输入提交信息
set /p msg="提交信息: "

REM 提交
git commit -m "%msg%"

REM 推送到GitHub
git push

echo.
echo ========================================
echo   构建并发布到 PyPI
echo ========================================
echo.

REM 构建
python -m build

REM 发布
twine upload dist/*

echo.
echo ✓ 发布完成！
pause
