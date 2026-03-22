#!/bin/bash
set -e

echo "==> Criando ambiente virtual (Python 3.13)..."
python3.13 -m venv venv

echo "==> Ativando ambiente virtual..."
source venv/bin/activate

echo "==> Instalando dependências..."
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

echo "==> Instalando navegador Chromium (Playwright)..."
playwright install chromium

echo ""
echo "==> Iniciando aplicação..."
python app.py
