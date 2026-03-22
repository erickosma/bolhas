"""
Unit tests for validate_url and GET / route.

Requisitos: 2.1, 2.2, 2.3, 7.1
"""

import pytest

from src.app import app, validate_url


class TestValidateUrl:
    """Testes unitários para a função validate_url."""

    def test_empty_url_returns_error(self):
        is_valid, msg = validate_url("")
        assert is_valid is False
        assert msg == "URL é obrigatória"

    def test_whitespace_only_url_returns_error(self):
        is_valid, msg = validate_url("   ")
        assert is_valid is False
        assert msg == "URL é obrigatória"

    def test_url_without_protocol_returns_error(self):
        is_valid, msg = validate_url("example.com")
        assert is_valid is False
        assert msg == "URL inválida"

    def test_url_with_http_is_valid(self):
        is_valid, msg = validate_url("http://example.com")
        assert is_valid is True
        assert msg == ""

    def test_url_with_https_is_valid(self):
        is_valid, msg = validate_url("https://example.com/product")
        assert is_valid is True
        assert msg == ""


class TestIndexRoute:
    """Testes unitários para a rota GET /."""

    @pytest.fixture
    def client(self):
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_get_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_get_index_contains_form(self, client):
        resp = client.get("/")
        assert b"<form" in resp.data
        assert b'name="url"' in resp.data
        assert b"Buscar produto" in resp.data
