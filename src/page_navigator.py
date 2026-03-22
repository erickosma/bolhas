import logging
import time

from src.selectors import COOKIE_ACCEPT_SELECTORS

logger = logging.getLogger(__name__)

TIMEOUT_MS = 60000


class PageNavigator:
    def __init__(self, page):
        self._page = page

    def load_page(self, url: str):
        self._page.goto(url, timeout=TIMEOUT_MS, wait_until="domcontentloaded")
        self._page.wait_for_load_state("load", timeout=TIMEOUT_MS)

    def dismiss_cookie_modal(self):
        for selector in COOKIE_ACCEPT_SELECTORS:
            if self._try_accept_cookie(selector):
                return

    def simulate_human_scroll(self):
        self._scroll_to_position("document.body.scrollHeight / 2")
        time.sleep(1)
        self._scroll_to_position("document.body.scrollHeight")
        time.sleep(1)
        self._scroll_to_position("0")
        time.sleep(0.5)

    def _try_accept_cookie(self, selector: str) -> bool:
        try:
            button = self._page.query_selector(selector)
            if not button:
                return False
            if not button.is_visible():
                return False
            button.click()
            logger.debug("Modal de cookies aceito via: %s", selector)
            return True
        except Exception as error:
            logger.debug("Erro ao tentar aceitar cookie com '%s': %s", selector, error)
            return False

    def _scroll_to_position(self, position: str):
        self._page.evaluate(
            f"window.scrollTo({{top: {position}, behavior: 'smooth'}})"
        )
