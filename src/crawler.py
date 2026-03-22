"""
Módulo de extração de dados de produtos via Playwright.

Expõe a função get_product_data(url) que gerencia o ciclo de vida
do navegador, executa navegação simulada e retorna os dados extraídos.
"""

import logging
import re
import time

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    ViewportSize,
)

logger = logging.getLogger(__name__)

TIMEOUT_MS = 60000  # 60 segundos

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

IMAGE_SELECTORS = [
    "#landingImage",                        # Amazon
    "#imgBlkFront",                         # Amazon (livros)
    "[data-testid='product-image'] img",
    ".product-image img",
    ".product-gallery img",
    "#product-image img",
    ".gallery-image img",
    "[data-zoom-image]",
    "img.product-image",
    "img[data-src]",
]


# Seletores comuns de modais de cookies para aceitar automaticamente
COOKIE_ACCEPT_SELECTORS = [
    "#sp-cc-accept",           # Amazon
    "#onetrust-accept-btn-handler",
    "[data-testid='cookie-accept']",
    "button[id*='cookie']",
    "button[id*='accept']",
]


def _extract_text(page, selectors: list[str]) -> str:
    """
    Tenta extrair texto usando uma lista de seletores CSS.
    Retorna o texto do primeiro seletor que encontrar um elemento,
    ou string vazia se nenhum for encontrado.
    """
    for selector in selectors:
        try:
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


def _extract_price_fallback(page) -> str:
    """
    Fallback para extração de preço quando os seletores CSS não encontram nada.
    Busca padrões de preço brasileiro (R$) no texto da página e retorna
    as linhas de preço concatenadas com " | " como separador.
    """
    try:
        body_text = page.inner_text("body")
    except Exception:
        return ""

    if not body_text:
        return ""

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]

    price_lines = []
    in_price_block = False

    for line in lines:
        has_price = bool(re.search(r"R\$\s?[\d]+[.,][\d]{2}", line))

        if has_price and not in_price_block:
            in_price_block = True
            price_lines.append(line)
        elif in_price_block:
            if has_price or re.search(
                r"(à vista|pix|parcela|cupom|juros|off|em até|pagamento|de:|por:?)",
                line,
                re.IGNORECASE,
            ):
                price_lines.append(line)
            else:
                break

    return " | ".join(price_lines) if price_lines else ""


def _extract_images(page) -> list[str]:
    """
    Extrai URLs das imagens principais do produto.
    Tenta seletores específicos primeiro, depois faz fallback
    para imagens grandes na página. Retorna lista de URLs únicas.
    """
    image_urls: list[str] = []
    seen: set[str] = set()

    def _add_url(url: str) -> None:
        if not url or url in seen:
            return
        # Ignorar placeholders, ícones e imagens tiny
        if any(skip in url.lower() for skip in ("placeholder", "icon", "sprite", "1x1", "pixel", "blank")):
            return
        seen.add(url)
        image_urls.append(url)

    # 1. Tentar seletores específicos de produto
    for selector in IMAGE_SELECTORS:
        try:
            elements = page.query_selector_all(selector)
            for el in elements:
                # Prioridade: data-zoom-image > data-old-hires > data-src > src
                for attr in ("data-zoom-image", "data-old-hires", "data-src", "src"):
                    src = el.get_attribute(attr)
                    if src and src.startswith("http"):
                        _add_url(src)
                        break
        except Exception:
            continue

    # 2. Fallback: imagens grandes (naturalWidth > 150) na página
    if not image_urls:
        try:
            large_imgs = page.evaluate("""
                () => {
                    const imgs = document.querySelectorAll('img');
                    const urls = [];
                    for (const img of imgs) {
                        if (img.naturalWidth > 150 && img.naturalHeight > 150) {
                            const src = img.dataset.src || img.src;
                            if (src && src.startsWith('http')) urls.push(src);
                        }
                    }
                    return urls;
                }
            """)
            for src in large_imgs:
                _add_url(src)
        except Exception:
            pass

    logger.debug("Extraídas %d imagens do produto", len(image_urls))
    return image_urls


def _dismiss_cookie_modal(page) -> None:
    """Tenta aceitar modais de cookies comuns sem bloquear."""
    for selector in COOKIE_ACCEPT_SELECTORS:
        try:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                btn.click()
                logger.debug("Modal de cookies aceito via: %s", selector)
                return
        except Exception:
            continue


def _simulate_navigation(page) -> None:
    """
    Simula navegação humana com scroll suave e delays
    para garantir carregamento de conteúdo lazy-loaded.
    """
    page.evaluate("window.scrollTo({top: document.body.scrollHeight / 2, behavior: 'smooth'})")
    time.sleep(1)
    page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
    time.sleep(1)
    page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
    time.sleep(0.5)


def get_product_data(
    url: str,
    cookies: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    """
    Função principal do crawler.

    Args:
        url: URL do produto a ser extraído.
        cookies: Cookies do navegador do usuário (chave: valor).
        headers: Headers HTTP do navegador do usuário.

    Retorna:
        dict com chaves "title", "price", "description" (todos str) em caso de sucesso.
        dict com chave "error" e "error_type" em caso de falha.
        error_type: "timeout", "connection", "extraction", "unknown"
    """
    logger.info("Iniciando extração para: %s", url)

    playwright_instance = None
    browser = None
    context = None
    page = None

    try:
        playwright_instance = sync_playwright().start()
        logger.debug("Playwright iniciado")

        browser = playwright_instance.chromium.launch(headless=True)
        logger.debug("Browser Chromium lançado (headless)")

        # Mesclar headers do usuário com user-agent padrão
        extra_headers = dict(headers) if headers else {}
        default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )

        context = browser.new_context(
            user_agent=extra_headers.pop("User-Agent", extra_headers.pop("user-agent", default_ua)),
            viewport=ViewportSize(width=1920, height=1080),
            extra_http_headers=extra_headers if extra_headers else None,
        )

        # Injetar cookies do usuário no contexto do browser
        if cookies:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            pw_cookies: list[dict] = [
                {
                    "name": name,
                    "value": value,
                    "domain": domain,
                    "path": "/",
                    "httpOnly": False,
                    "secure": url.startswith("https"),
                    "sameSite": "Lax",
                }
                for name, value in cookies.items()
            ]
            context.add_cookies(pw_cookies)  # type: ignore[arg-type]
            logger.debug("Injetados %d cookies do usuário para domínio %s", len(pw_cookies), domain)

        page = context.new_page()

        # Navegar com domcontentloaded (mais confiável que networkidle)
        page.goto(url, timeout=TIMEOUT_MS, wait_until="domcontentloaded")
        # Aguardar estabilização adicional do DOM
        page.wait_for_load_state("load", timeout=TIMEOUT_MS)
        logger.debug("Página carregada: %s", url)

        # Aceitar cookies se modal aparecer
        _dismiss_cookie_modal(page)

        # Navegação simulada (scroll + delays)
        _simulate_navigation(page)

        # Extrair dados via seletores
        title = _extract_text(page, TITLE_SELECTORS)
        price = _extract_text(page, PRICE_SELECTORS)

        if not price:
            logger.info("Seletores CSS não encontraram preço, usando fallback regex")
            price = _extract_price_fallback(page)

        description = _extract_text(page, DESCRIPTION_SELECTORS)

        images = _extract_images(page)

        result = {
            "title": title,
            "price": price,
            "description": description,
            "images": images,
        }

        if not title and not price and not description:
            logger.warning("Nenhum dado extraído para: %s", url)
            return {
                "error": "Não foi possível extrair dados desta página",
                "error_type": "extraction",
            }

        logger.info("Extração concluída com sucesso para: %s", url)
        return result

    except PlaywrightTimeoutError:
        msg = "Timeout: a página não carregou em 60 segundos"
        logger.error("Timeout ao acessar: %s", url)
        return {"error": msg, "error_type": "timeout"}

    except Exception as exc:
        error_str = str(exc).lower()
        if any(k in error_str for k in ("net::err", "connection", "dns", "econnrefused")):
            msg = "Falha de conexão: não foi possível acessar a URL"
            logger.error("Erro de conexão para %s: %s", url, exc)
            return {"error": msg, "error_type": "connection"}

        msg = "Erro inesperado ao processar a página"
        logger.error("Erro inesperado para %s: %s: %s", url, type(exc).__name__, exc)
        return {"error": msg, "error_type": "unknown"}

    finally:
        for resource, name in [(page, "page"), (context, "context"), (browser, "browser")]:
            if resource:
                try:
                    resource.close()
                    logger.debug("%s fechado", name)
                except Exception as e:
                    logger.warning("Erro ao fechar %s: %s", name, e)
        if playwright_instance:
            try:
                playwright_instance.stop()
                logger.debug("Playwright encerrado")
            except Exception as e:
                logger.warning("Erro ao encerrar Playwright: %s", e)
