from unittest.mock import MagicMock, patch

from src.browser_session import BrowserSession, DEFAULT_USER_AGENT


class TestBrowserSessionResolveHeaders:
    def test_returns_default_user_agent_when_no_headers(self):
        session = BrowserSession()
        user_agent, extra = session._resolve_headers(None)
        assert user_agent == DEFAULT_USER_AGENT
        assert extra == {}

    def test_extracts_user_agent_from_headers(self):
        session = BrowserSession()
        headers = {"User-Agent": "Custom/1.0", "Accept": "text/html"}
        user_agent, extra = session._resolve_headers(headers)
        assert user_agent == "Custom/1.0"
        assert "User-Agent" not in extra
        assert extra["Accept"] == "text/html"

    def test_handles_lowercase_user_agent(self):
        session = BrowserSession()
        headers = {"user-agent": "Custom/2.0"}
        user_agent, extra = session._resolve_headers(headers)
        assert user_agent == "Custom/2.0"


class TestBrowserSessionClose:
    def test_close_handles_none_resources(self):
        session = BrowserSession()
        session.close()

    def test_close_handles_resource_exception(self):
        session = BrowserSession()
        mock_page = MagicMock()
        mock_page.close.side_effect = Exception("Already closed")
        session._page = mock_page
        session.close()


class TestBrowserSessionInjectCookies:
    def test_builds_correct_cookie_structure(self):
        session = BrowserSession()
        session._context = MagicMock()

        cookies = {"session_id": "abc123", "theme": "dark"}
        session._inject_cookies(cookies, "https://example.com/product")

        call_args = session._context.add_cookies.call_args[0][0]
        assert len(call_args) == 2

        first_cookie = call_args[0]
        assert first_cookie["name"] == "session_id"
        assert first_cookie["value"] == "abc123"
        assert first_cookie["domain"] == "example.com"
        assert first_cookie["secure"] is True
        assert first_cookie["sameSite"] == "Lax"

    def test_sets_secure_false_for_http(self):
        session = BrowserSession()
        session._context = MagicMock()

        session._inject_cookies({"key": "val"}, "http://example.com")

        call_args = session._context.add_cookies.call_args[0][0]
        assert call_args[0]["secure"] is False
