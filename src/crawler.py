import logging

from src.browser_session import BrowserSession
from src.page_navigator import PageNavigator
from src.product_scraper import ProductScraper
from src.error_classifier import ErrorClassifier

logger = logging.getLogger(__name__)


def get_product_data(
    url: str,
    cookies: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    logger.info("Iniciando extração para: %s", url)

    session = BrowserSession()
    error_classifier = ErrorClassifier()

    try:
        page = session.start(
            cookies=cookies,
            headers=headers,
            target_url=url,
        )

        navigator = PageNavigator(page)
        navigator.load_page(url)
        navigator.dismiss_cookie_modal()
        navigator.simulate_human_scroll()

        scraper = ProductScraper(page)
        result = scraper.extract_product()

        logger.info("Extração concluída para: %s", url)
        return result

    except Exception as exception:
        return error_classifier.classify(exception, url)

    finally:
        session.close()
