import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    def __init__(self, page):
        self._page = page

    def find_first_match(self, selectors: list[str]) -> str:
        for selector in selectors:
            text = self._try_selector(selector)
            if text:
                return text
        return ""

    def _try_selector(self, selector: str) -> str:
        try:
            if selector.startswith("meta["):
                return self._extract_meta_content(selector)
            return self._extract_inner_text(selector)
        except Exception as error:
            logger.debug("Erro ao extrair texto com seletor '%s': %s", selector, error)
            return ""

    def _extract_meta_content(self, selector: str) -> str:
        element = self._page.query_selector(selector)
        if not element:
            return ""
        content = element.get_attribute("content")
        if not content:
            return ""
        return content.strip()

    def _extract_inner_text(self, selector: str) -> str:
        element = self._page.query_selector(selector)
        if not element:
            return ""
        text = element.inner_text()
        if not text:
            return ""
        return text.strip()
