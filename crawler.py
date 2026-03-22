"""
Módulo de extração de dados de produtos via Playwright.

Expõe a função get_product_data(url) que gerencia o ciclo de vida
do navegador, executa navegação simulada e retorna os dados extraídos.

Requisitos: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5,
            5.1, 5.2, 6.1, 6.2, 6.3, 9.1, 9.2, 9.3, 10.1, 10.2
"""

import logging
import re
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

TIMEOUT_MS = 30000  # 30 segundos

TITLE_SELECTORS = [
    "h1.product-title",
    "h1.product-name",
    "h1#productTitle",
    "[data-testid='product-title']",
    "h1",
    ".product-title",
]

PRICE_SELECTORS = [
    ".price",
    ".product-price",
    "#priceblock_ourprice",
    "[data-testid='price']",
    ".offer-price",
    "span.price",
]

DESCRIPTION_SELECTORS = [
    ".product-description",
    "#productDescription",
    "[data-testid='product-description']",
    ".description",
    "#feature-bullets",
    "meta[name='description']",
]


def _extract_text(page, selectors: list[str]) -> str:
    """
    Tenta extrair texto usando uma lista de seletores CSS.
    Retorna o texto do primeiro seletor que encontrar um elemento,
    ou string vazia se nenhum for encontrado.
    """
    for selector in selectors:
        try:
            # Tratamento especial para meta tags
            if selector.startswith("meta["):
                element = page.query_selector(selector)
                if element:
                    content = element.get_attribute("content")
                    if content and content.strip():
                        return content.strip()
                continue

            element = page.query_selector(selector)
            if element:
                text = element.inner_text()
                if text and text.strip():
                    return text.strip()
        except Exception:
            continue
    return ""


def _extract_price_fallback(page) -> list[str]:
    """
    Fallback para extração de preço quando os seletores CSS não encontram nada.
    Busca padrões de preço brasileiro (R$) no texto da página e retorna
    uma lista de linhas de preço contextualizadas.

    Ex: ["R$237,40", "à vista no Pix (5% off)", "ou R$ 249,90 em até 6x de R$ 41,65"]
    """
    try:
        body_text = page.inner_text("body")
    except Exception:
        return []

    if not body_text:
        return []

    # Quebrar o texto em linhas e encontrar o bloco com preços R$
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]

    price_lines = []
    in_price_block = False

    for line in lines:
        has_price = bool(re.search(r"R\$\s?[\d]+[.,][\d]{2}", line))

        if has_price and not in_price_block:
            in_price_block = True
            price_lines.append(line)
        elif in_price_block:
            # Continuar capturando linhas do bloco de preço
            # (à vista, parcelas, cupom, etc.)
            if has_price or re.search(
                r"(à vista|pix|parcela|cupom|juros|off|em até|pagamento|de:|por:?)",
                line,
                re.IGNORECASE,
            ):
                price_lines.append(line)
            else:
                # Fim do bloco de preço
                break

    return price_lines if price_lines else []




def _simulate_navigation(page) -> None:
    """
    Simula navegação humana com scroll e delays para garantir
    carregamento de conteúdo lazy-loaded.
    """
    # Scroll gradual pela página
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    time.sleep(1)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    # Volta ao topo
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)


def get_product_data(url: str) -> dict:
    """
    Função principal do crawler.

    Parâmetros:
        url: URL do produto (já validada)

    Retorna:
        dict com chaves "title", "price", "description" em caso de sucesso.
        dict com chave "error" em caso de falha.
    """
    logger.info("Iniciando extração de dados para URL: %s", url)

    browser = None
    playwright_instance = None
    try:
        playwright_instance = sync_playwright().start()
        browser = playwright_instance.chromium.launch(headless=False)
        page = browser.new_page()

        # Navegar até a URL com timeout
        page.goto(url, timeout=TIMEOUT_MS, wait_until="domcontentloaded")

        # Aguardar carregamento completo do DOM
        page.wait_for_load_state("domcontentloaded")

        # Navegação simulada (scroll + delays)
        _simulate_navigation(page)

        # Extrair dados via seletores
        title = _extract_text(page, TITLE_SELECTORS)
        price = _extract_text(page, PRICE_SELECTORS)
        if not price:
            logger.info("Seletores CSS não encontraram preço, usando fallback regex")
            price_lines = _extract_price_fallback(page)
            price = price_lines if price_lines else ""
        description = _extract_text(page, DESCRIPTION_SELECTORS)

        result = {
            "title": title,
            "price": price,
            "description": description,
        }

        logger.info("Extração concluída com sucesso para URL: %s", url)
        return result

    except PlaywrightTimeoutError:
        error_msg = "Timeout: a página não carregou em 30 segundos"
        logger.error("Erro de timeout ao acessar URL: %s - %s", url, error_msg)
        return {"error": error_msg}

    except Exception as exc:
        error_str = str(exc).lower()
        if "net::err" in error_str or "connection" in error_str or "dns" in error_str:
            error_msg = "Falha de conexão: não foi possível acessar a URL"
            logger.error("Erro de conexão ao acessar URL: %s - %s", url, error_msg)
            return {"error": error_msg}

        error_msg = "Erro inesperado ao processar a página"
        logger.error(
            "Erro inesperado ao acessar URL: %s - %s: %s",
            url,
            type(exc).__name__,
            exc,
        )
        return {"error": error_msg}

    finally:
        if browser:
            browser.close()
        if playwright_instance:
            playwright_instance.stop()
