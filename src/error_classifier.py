import logging

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

CONNECTION_KEYWORDS = ("net::err", "connection", "dns", "econnrefused")


class ErrorClassifier:
    def classify(self, exception: Exception, url: str) -> dict:
        if isinstance(exception, PlaywrightTimeoutError):
            return self._timeout_error(url)

        if self._is_connection_error(exception):
            return self._connection_error(url, exception)

        return self._unknown_error(url, exception)

    def _timeout_error(self, url: str) -> dict:
        logger.error("Timeout ao acessar: %s", url)
        return {
            "error": "Timeout: a página não carregou em 60 segundos",
            "error_type": "timeout",
        }

    def _connection_error(self, url: str, exception: Exception) -> dict:
        logger.error("Erro de conexão para %s: %s", url, exception)
        return {
            "error": "Falha de conexão: não foi possível acessar a URL",
            "error_type": "connection",
        }

    def _unknown_error(self, url: str, exception: Exception) -> dict:
        logger.error(
            "Erro inesperado para %s: %s: %s",
            url, type(exception).__name__, exception,
        )
        return {
            "error": "Erro inesperado ao processar a página",
            "error_type": "unknown",
        }

    def _is_connection_error(self, exception: Exception) -> bool:
        error_message = str(exception).lower()
        for keyword in CONNECTION_KEYWORDS:
            if keyword in error_message:
                return True
        return False
