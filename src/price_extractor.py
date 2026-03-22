import logging
import re

from src.selectors import PRICE_SELECTORS
from src.text_extractor import TextExtractor

logger = logging.getLogger(__name__)

PRICE_PATTERN = re.compile(r"R\$\s?[\d]+[.,][\d]{2}")
PRICE_CONTEXT_PATTERN = re.compile(
    r"(à vista|pix|parcela|cupom|juros|off|em até|pagamento|de:|por:?)",
    re.IGNORECASE,
)


class PriceExtractor:
    def __init__(self, page):
        self._page = page
        self._text_extractor = TextExtractor(page)

    def extract(self) -> str:
        price_from_selector = self._text_extractor.find_first_match(PRICE_SELECTORS)
        if price_from_selector:
            return price_from_selector

        logger.info("Seletores CSS não encontraram preço, usando fallback regex")
        return self._extract_from_page_text()

    def _extract_from_page_text(self) -> str:
        body_text = self._read_body_text()
        if not body_text:
            return ""

        non_empty_lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]
        return self._collect_price_block(non_empty_lines)

    def _read_body_text(self) -> str:
        try:
            return self._page.inner_text("body")
        except Exception as error:
            logger.debug("Erro ao ler texto do body: %s", error)
            return ""

    def _collect_price_block(self, lines: list[str]) -> str:
        price_lines: list[str] = []
        found_first_price = False

        for line in lines:
            is_price_line = bool(PRICE_PATTERN.search(line))

            if is_price_line and not found_first_price:
                found_first_price = True
                price_lines.append(line)
                continue

            if not found_first_price:
                continue

            if self._is_price_related(line, is_price_line):
                price_lines.append(line)
                continue

            break

        if not price_lines:
            return ""
        return " | ".join(price_lines)

    @staticmethod
    def _is_price_related(line: str, has_price: bool) -> bool:
        if has_price:
            return True
        return bool(PRICE_CONTEXT_PATTERN.search(line))
