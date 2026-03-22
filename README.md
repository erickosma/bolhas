# Product Crawler

Aplicação web para extração de dados de produtos (título, preço e descrição) a partir de URLs. Utiliza Playwright para simular navegação humana e Flask para servir a interface.

## Tecnologias

- Python 3.10+
- Flask — framework web
- Playwright — automação de navegador (Chromium headless)
- Jinja2 — templates HTML
- HTML + CSS — frontend
- pytest + hypothesis — testes unitários e property-based

## Estrutura do Projeto

```
src/
  app.py                # Backend Flask (rotas e validação)
  crawler.py            # Módulo de extração via Playwright
  templates/
    index.html          # Página inicial com formulário
    result.html         # Página de resultados
  static/
    style.css           # Estilos
tests/
  test_app.py           # Testes unitários
  test_validate_url_property.py
  test_product_data_property.py
  test_result_template_property.py
  test_scrape_route.py
```

## Como Executar

```bash
# 1. Criar ambiente virtual
python3.13 -m venv venv

# 2. Ativar o ambiente
# macOS/Linux:
source venv/bin/activate
# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar navegador do Playwright
playwright install chromium

# 5. Rodar a aplicação
python -m src.app
```

A aplicação estará disponível em `http://127.0.0.1:5000`.

## Como Testar

```bash
pytest tests/ -v
```
