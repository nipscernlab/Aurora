@echo off
:: surfer_loader.bat - Script para Windows
:: Uso: surfer_loader.bat arquivo.vcd

if "%1"=="" (
    echo Uso: surfer_loader.bat arquivo.vcd
    pause
    exit /b 1
)

if not exist "%1" (
    echo Erro: Arquivo %1 nao encontrado!
    pause
    exit /b 1
)

echo Carregando %1 no Surfer...
python surfer_loader.py "%1"

if errorlevel 1 (
    echo Erro ao executar o script Python
    pause
    exit /b 1
)

echo.
echo Surfer iniciado! Pressione qualquer tecla para fechar.
pause > nul

---

#!/bin/bash
# surfer_loader.sh - Script para Linux/Mac
# Uso: ./surfer_loader.sh arquivo.vcd

if [ $# -eq 0 ]; then
    echo "Uso: ./surfer_loader.sh arquivo.vcd"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Erro: Arquivo $1 não encontrado!"
    exit 1
fi

echo "Carregando $1 no Surfer..."
python3 surfer_loader.py "$1"

if [ $? -ne 0 ]; then
    echo "Erro ao executar o script Python"
    exit 1
fi

echo "Surfer iniciado!"