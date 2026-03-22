from src.app import app
from src.request_context import RequestContext


class TestRequestContextCookies:
    def test_extracts_cookies_from_request(self):
        context = RequestContext()
        with app.test_request_context(
            "/scrape",
            method="POST",
            headers={"Cookie": "session=abc123; theme=dark"},
        ):
            cookies = context.extract_cookies()
            assert cookies["session"] == "abc123"
            assert cookies["theme"] == "dark"

    def test_returns_empty_dict_when_no_cookies(self):
        context = RequestContext()
        with app.test_request_context("/scrape", method="POST"):
            cookies = context.extract_cookies()
            assert cookies == {}


class TestRequestContextHeaders:
    def test_extracts_headers_excluding_internal(self):
        context = RequestContext()
        with app.test_request_context(
            "/scrape",
            method="POST",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "pt-BR",
                "Host": "localhost",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ):
            headers = context.extract_headers()
            assert "User-Agent" in headers
            assert "Accept-Language" in headers
            assert "Host" not in headers
            assert "Content-Type" not in headers

    def test_excludes_connection_header(self):
        context = RequestContext()
        with app.test_request_context(
            "/scrape",
            method="POST",
            headers={"Connection": "keep-alive", "Accept": "text/html"},
        ):
            headers = context.extract_headers()
            assert "Connection" not in headers
            assert "Accept" in headers
