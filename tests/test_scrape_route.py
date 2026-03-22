"""
Unit tests for POST /scrape route.

Requisitos: 7.2, 7.3, 8.2
"""

from unittest.mock import patch

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestScrapeRouteInvalidUrl:
    """Testes para POST /scrape com URL inválida."""

    def test_post_empty_url_returns_index_with_error(self, client):
        resp = client.post("/scrape", data={"url": ""})
        assert resp.status_code == 200
        assert "URL é obrigatória".encode() in resp.data

    def test_post_invalid_url_returns_index_with_error(self, client):
        resp = client.post("/scrape", data={"url": "not-a-url"})
        assert resp.status_code == 200
        assert "URL inválida".encode() in resp.data


class TestScrapeRouteValidUrl:
    """Testes para POST /scrape com URL válida (mock do crawler)."""

    def test_post_valid_url_returns_result_with_data(self, client):
        mock_data = {
            "title": "Produto Teste",
            "price": "R$ 99,90",
            "description": "Descrição do produto teste",
        }
        with patch("src.app.get_product_data", return_value=mock_data):
            resp = client.post("/scrape", data={"url": "https://example.com/product"})
            assert resp.status_code == 200
            assert b"Produto Teste" in resp.data
            assert "R$ 99,90".encode() in resp.data
            assert "Descrição do produto teste".encode() in resp.data

    def test_post_valid_url_crawler_error_shows_error(self, client):
        mock_error = {"error": "Timeout: a página não carregou em 30 segundos"}
        with patch("src.app.get_product_data", return_value=mock_error):
            resp = client.post("/scrape", data={"url": "https://example.com/slow"})
            assert resp.status_code == 200
            assert "Timeout".encode() in resp.data


class TestResultPageBackLink:
    """Testa que result.html contém link de retorno para /."""

    def test_result_page_contains_back_link(self, client):
        mock_data = {
            "title": "Produto",
            "price": "R$ 10",
            "description": "Desc",
        }
        with patch("src.app.get_product_data", return_value=mock_data):
            resp = client.post("/scrape", data={"url": "https://example.com"})
            assert resp.status_code == 200
            assert b'href="/"' in resp.data
            assert "Voltar".encode() in resp.data
