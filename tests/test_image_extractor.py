from unittest.mock import MagicMock

from src.image_extractor import ImageExtractor


class TestImageExtractorFromSelectors:
    def test_extracts_image_from_src_attribute(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = (
            lambda attr: "https://img.example.com/product.jpg" if attr == "src" else None
        )

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert "https://img.example.com/product.jpg" in result

    def test_prefers_data_zoom_image_over_src(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = lambda attr: {
            "data-zoom-image": "https://img.example.com/zoom.jpg",
            "src": "https://img.example.com/thumb.jpg",
        }.get(attr)

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert "https://img.example.com/zoom.jpg" in result
        assert "https://img.example.com/thumb.jpg" not in result

    def test_deduplicates_urls(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = (
            lambda attr: "https://img.example.com/same.jpg" if attr == "src" else None
        )

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element, mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert len(result) == 1


class TestImageExtractorIgnorePatterns:
    def test_ignores_placeholder_images(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = (
            lambda attr: "https://example.com/placeholder.png" if attr == "src" else None
        )

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert len(result) == 0

    def test_ignores_icon_images(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = (
            lambda attr: "https://example.com/icon-star.svg" if attr == "src" else None
        )

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert len(result) == 0


class TestImageExtractorFallback:
    def test_falls_back_to_large_images_when_selectors_empty(self):
        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = []
        mock_page.evaluate.return_value = ["https://img.example.com/large.jpg"]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert "https://img.example.com/large.jpg" in result

    def test_skips_fallback_when_selectors_found_images(self):
        mock_element = MagicMock()
        mock_element.get_attribute.side_effect = (
            lambda attr: "https://img.example.com/product.jpg" if attr == "src" else None
        )

        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_element]

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        mock_page.evaluate.assert_not_called()

    def test_handles_evaluate_exception(self):
        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = []
        mock_page.evaluate.side_effect = Exception("JS error")

        extractor = ImageExtractor(mock_page)
        result = extractor.extract()
        assert result == []
