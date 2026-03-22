from unittest.mock import MagicMock

from src.price_extractor import PriceExtractor


class TestPriceExtractorFromSelector:
    def test_returns_price_from_css_selector(self):
        mock_element = MagicMock()
        mock_element.inner_text.return_value = "R$ 99,90"

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_element

        extractor = PriceExtractor(mock_page)
        result = extractor.extract()
        assert result == "R$ 99,90"


class TestPriceExtractorFallback:
    def test_fallback_extracts_price_from_body_text(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None
        mock_page.inner_text.return_value = (
            "Algum texto\n"
            "R$132,90\n"
            "à vista no Pix (5% off)\n"
            "ou R$ 139,90 em até 6x\n"
            "Outras informações"
        )

        extractor = PriceExtractor(mock_page)
        result = extractor.extract()
        assert "R$132,90" in result
        assert "à vista no Pix" in result
        assert "R$ 139,90" in result

    def test_fallback_returns_empty_when_no_price(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None
        mock_page.inner_text.return_value = "Texto sem preço nenhum"

        extractor = PriceExtractor(mock_page)
        result = extractor.extract()
        assert result == ""

    def test_fallback_stops_at_unrelated_line(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None
        mock_page.inner_text.return_value = (
            "R$50,00\n"
            "Adicionar ao carrinho\n"
            "R$100,00"
        )

        extractor = PriceExtractor(mock_page)
        result = extractor.extract()
        assert result == "R$50,00"

    def test_fallback_handles_body_read_exception(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None
        mock_page.inner_text.side_effect = Exception("Page crashed")

        extractor = PriceExtractor(mock_page)
        result = extractor.extract()
        assert result == ""
