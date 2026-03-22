from unittest.mock import MagicMock

from src.text_extractor import TextExtractor


class TestTextExtractorInnerText:
    def test_returns_text_from_first_matching_selector(self):
        mock_element = MagicMock()
        mock_element.inner_text.return_value = "Produto Teste"

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_element

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["h1"])
        assert result == "Produto Teste"

    def test_skips_empty_elements(self):
        empty_element = MagicMock()
        empty_element.inner_text.return_value = ""

        valid_element = MagicMock()
        valid_element.inner_text.return_value = "Encontrado"

        mock_page = MagicMock()
        mock_page.query_selector.side_effect = [empty_element, valid_element]

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match([".empty", ".valid"])
        assert result == "Encontrado"

    def test_returns_empty_when_no_match(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["h1", ".title"])
        assert result == ""

    def test_strips_whitespace(self):
        mock_element = MagicMock()
        mock_element.inner_text.return_value = "  Texto com espaços  "

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_element

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["h1"])
        assert result == "Texto com espaços"


class TestTextExtractorMetaContent:
    def test_extracts_meta_content_attribute(self):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "Descrição do produto"

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_element

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["meta[name='description']"])
        assert result == "Descrição do produto"

    def test_skips_meta_with_empty_content(self):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = ""

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_element

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["meta[name='description']"])
        assert result == ""


class TestTextExtractorExceptionHandling:
    def test_handles_exception_gracefully(self):
        mock_page = MagicMock()
        mock_page.query_selector.side_effect = Exception("DOM error")

        extractor = TextExtractor(mock_page)
        result = extractor.find_first_match(["h1"])
        assert result == ""
