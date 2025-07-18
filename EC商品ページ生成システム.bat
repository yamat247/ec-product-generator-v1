@echo off
echo 🚀 EC商品ページ自動作成システム 起動中...
echo ================================
cd /d "%USERPROFILE%\Documents\ec-product-generator"
echo プロジェクトフォルダに移動しました
echo.
echo システムを起動しています...
python app.py
pause