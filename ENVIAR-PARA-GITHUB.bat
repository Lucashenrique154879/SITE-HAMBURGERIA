@echo off
cd /d "%~dp0"
git remote remove origin 2>nul
git remote add origin https://github.com/Lucashenrique154879/SITE-HAMBURGERIA.git
git branch -M main
git push -u origin main --force
pause
