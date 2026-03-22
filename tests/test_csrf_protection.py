import pytest

from src.app import app


class TestCsrfProtection:
    @pytest.fixture
    def client_with_csrf(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = True
        with app.test_client() as client:
            yield client
        app.config["WTF_CSRF_ENABLED"] = False

    def test_post_without_csrf_token_returns_400(self, client_with_csrf):
        response = client_with_csrf.post(
            "/scrape",
            data={"url": "https://example.com"},
        )
        assert response.status_code == 400

    def test_index_contains_csrf_token_field(self, client_with_csrf):
        response = client_with_csrf.get("/")
        assert b"csrf_token" in response.data
