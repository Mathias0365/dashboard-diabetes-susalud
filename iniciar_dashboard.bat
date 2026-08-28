@echo off
rem Lanzador del Dashboard de Diabetes SUSALUD
rem Abre el navegador y luego inicia el servidor (mantener esta ventana abierta)
cd /d "%~dp0"
start "" http://localhost:8050
python "%~dp0app.py"
pause
