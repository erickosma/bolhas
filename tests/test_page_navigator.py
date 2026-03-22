from unittest.mock import MagicMock, patch

from src.page_navigator import PageNavigator, TIMEOUT_MS


class TestPageNavigatorLoadPage:
    def test_calls_goto_with_correct_params(self):
        mock_page = MagicMock()
        navigator = PageNavigator(mock_page)
        navigator.load_page("https://example.com")

        mock_page.goto.assert_called_once_with(
            "https://example.com",
            timeout=TIMEOUT_MS,
            wait_until="domcontentloaded",
        )

    def test_waits_for_load_state(self):
        mock_page = MagicMock()
        navigator = PageNavigator(mock_page)
        navigator.load_page("https://example.com")

        mock_page.wait_for_load_state.assert_called_once_with(
            "load", timeout=TIMEOUT_MS,
        )


class TestPageNavigatorCookieModal:
    def test_clicks_visible_cookie_button(self):
        mock_button = MagicMock()
        mock_button.is_visible.return_value = True

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_button

        navigator = PageNavigator(mock_page)
        navigator.dismiss_cookie_modal()

        mock_button.click.assert_called_once()

    def test_skips_invisible_button(self):
        mock_button = MagicMock()
        mock_button.is_visible.return_value = False

        mock_page = MagicMock()
        mock_page.query_selector.return_value = mock_button

        navigator = PageNavigator(mock_page)
        navigator.dismiss_cookie_modal()

        mock_button.click.assert_not_called()

    def test_handles_no_cookie_modal(self):
        mock_page = MagicMock()
        mock_page.query_selector.return_value = None

        navigator = PageNavigator(mock_page)
        navigator.dismiss_cookie_modal()


class TestPageNavigatorScroll:
    @patch("src.page_navigator.time")
    def test_scrolls_three_positions(self, mock_time):
        mock_page = MagicMock()
        navigator = PageNavigator(mock_page)
        navigator.simulate_human_scroll()

        assert mock_page.evaluate.call_count == 3
        assert mock_time.sleep.call_count == 3
