import logging

from src.selectors import TITLE_SELECTORS, DESCRIPTION_SELECTORS
from src.text_extractor import TextExtractor
from src.price_extractor import PriceExtractor
from src.image_extractor import ImageExtractor

logger = logging.getLogger(__name__)


class ProductScraper:
    def __init__(self, page):
        self._page = page
        self._text_extractor = TextExtractor(page)
        self._price_extractor = PriceExtractor(page)
        self._image_extractor = ImageExtractor(page)

    def extract_product(self) -> dict:
        title = self._text_extractor.find_first_match(TITLE_SELECTORS)
        price = self._price_extractor.extract()
        description = self._text_extractor.find_first_match(DESCRIPTION_SELECTORS)
        images = self._image_extractor.extract()

        if not title and not price and not description:
            logger.warning("Nenhum dado extraído da página")
            return {
                "error": "Não foi possível extrair dados desta página",
                "error_type": "extraction",
            }

        return {
            "title": title,
            "price": price,
            "description": description,
            "images": images,
        }
