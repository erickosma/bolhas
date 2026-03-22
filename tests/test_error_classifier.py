from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.error_classifier import ErrorClassifier


class TestErrorClassifierTimeout:
    def test_playwright_timeout_returns_timeout_type(self):
        classifier = ErrorClassifier()
        timeout_error = PlaywrightTimeoutError("Timeout 60000ms exceeded")
        result = classifier.classify(timeout_error, "https://example.com")
        assert result["error_type"] == "timeout"
        assert "60 segundos" in result["error"]

    def test_timeout_error_contains_error_key(self):
        classifier = ErrorClassifier()
        timeout_error = PlaywrightTimeoutError("Timeout")
        result = classifier.classify(timeout_error, "https://example.com")
        assert "error" in result


class TestErrorClassifierConnection:
    def test_net_err_is_connection_error(self):
        classifier = ErrorClassifier()
        error = Exception("net::ERR_NAME_NOT_RESOLVED")
        result = classifier.classify(error, "https://example.com")
        assert result["error_type"] == "connection"

    def test_dns_is_connection_error(self):
        classifier = ErrorClassifier()
        error = Exception("DNS resolution failed")
        result = classifier.classify(error, "https://example.com")
        assert result["error_type"] == "connection"

    def test_econnrefused_is_connection_error(self):
        classifier = ErrorClassifier()
        error = Exception("ECONNREFUSED 127.0.0.1:443")
        result = classifier.classify(error, "https://example.com")
        assert result["error_type"] == "connection"


class TestErrorClassifierUnknown:
    def test_generic_exception_is_unknown(self):
        classifier = ErrorClassifier()
        error = Exception("Something weird happened")
        result = classifier.classify(error, "https://example.com")
        assert result["error_type"] == "unknown"
        assert "Erro inesperado" in result["error"]

    def test_value_error_is_unknown(self):
        classifier = ErrorClassifier()
        error = ValueError("bad value")
        result = classifier.classify(error, "https://example.com")
        assert result["error_type"] == "unknown"
