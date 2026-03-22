import logging

from src.selectors import (
    IMAGE_SELECTORS,
    IMAGE_PRIORITY_ATTRIBUTES,
    IMAGE_IGNORE_PATTERNS,
)

logger = logging.getLogger(__name__)

LARGE_IMAGE_JS = """
() => {
    const images = document.querySelectorAll('img');
    const urls = [];
    for (const image of images) {
        if (image.naturalWidth > 150 && image.naturalHeight > 150) {
            const source = image.dataset.src || image.src;
            if (source && source.startsWith('http')) urls.push(source);
        }
    }
    return urls;
}
"""


class ImageExtractor:
    def __init__(self, page):
        self._page = page
        self._found_urls: list[str] = []
        self._seen_urls: set[str] = set()

    def extract(self) -> list[str]:
        self._collect_from_selectors()

        if not self._found_urls:
            self._collect_large_images()

        logger.debug("Extraídas %d imagens do produto", len(self._found_urls))
        return self._found_urls

    def _collect_from_selectors(self):
        for selector in IMAGE_SELECTORS:
            self._try_selector(selector)

    def _try_selector(self, selector: str):
        try:
            elements = self._page.query_selector_all(selector)
            for element in elements:
                self._extract_best_url(element)
        except Exception as error:
            logger.debug("Erro ao buscar imagens com seletor '%s': %s", selector, error)

    def _extract_best_url(self, element):
        for attribute in IMAGE_PRIORITY_ATTRIBUTES:
            source_url = element.get_attribute(attribute)
            if not source_url:
                continue
            if not source_url.startswith("http"):
                continue
            self._register_url(source_url)
            return

    def _collect_large_images(self):
        try:
            large_image_urls = self._page.evaluate(LARGE_IMAGE_JS)
            for source_url in large_image_urls:
                self._register_url(source_url)
        except Exception as error:
            logger.debug("Erro ao buscar imagens grandes via JS: %s", error)

    def _register_url(self, url: str):
        if url in self._seen_urls:
            return
        if self._is_ignorable(url):
            return
        self._seen_urls.add(url)
        self._found_urls.append(url)

    def _is_ignorable(self, url: str) -> bool:
        lower_url = url.lower()
        for pattern in IMAGE_IGNORE_PATTERNS:
            if pattern in lower_url:
                return True
        return False
