from unittest.mock import MagicMock, patch

from src.product_scraper import ProductScraper


class TestProductScraperSuccess:
    def test_returns_product_dict_with_all_fields(self):
        mock_page = MagicMock()

        with patch("src.product_scraper.TextExtractor") as MockText, \
             patch("src.product_scraper.PriceExtractor") as MockPrice, \
             patch("src.product_scraper.ImageExtractor") as MockImage:

            MockText.return_value.find_first_match.side_effect = [
                "Café Especial",
                "Descrição do café",
            ]
            MockPrice.return_value.extract.return_value = "R$ 29,90"
            MockImage.return_value.extract.return_value = ["https://img.example.com/cafe.jpg"]

            scraper = ProductScraper(mock_page)
            result = scraper.extract_product()

            assert result["title"] == "Café Especial"
            assert result["price"] == "R$ 29,90"
            assert result["description"] == "Descrição do café"
            assert result["images"] == ["https://img.example.com/cafe.jpg"]


class TestProductScraperExtractionFailure:
    def test_returns_error_when_all_fields_empty(self):
        mock_page = MagicMock()

        with patch("src.product_scraper.TextExtractor") as MockText, \
             patch("src.product_scraper.PriceExtractor") as MockPrice, \
             patch("src.product_scraper.ImageExtractor") as MockImage:

            MockText.return_value.find_first_match.return_value = ""
            MockPrice.return_value.extract.return_value = ""
            MockImage.return_value.extract.return_value = []

            scraper = ProductScraper(mock_page)
            result = scraper.extract_product()

            assert "error" in result
            assert result["error_type"] == "extraction"


class TestProductScraperPartialData:
    def test_returns_product_when_only_title_found(self):
        mock_page = MagicMock()

        with patch("src.product_scraper.TextExtractor") as MockText, \
             patch("src.product_scraper.PriceExtractor") as MockPrice, \
             patch("src.product_scraper.ImageExtractor") as MockImage:

            MockText.return_value.find_first_match.side_effect = ["Produto", ""]
            MockPrice.return_value.extract.return_value = ""
            MockImage.return_value.extract.return_value = []

            scraper = ProductScraper(mock_page)
            result = scraper.extract_product()

            assert "error" not in result
            assert result["title"] == "Produto"
