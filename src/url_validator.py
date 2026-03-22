import ipaddress
from urllib.parse import urlparse

VALID_PROTOCOLS = ("http://", "https://")

BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "metadata.google.internal",
    "169.254.169.254",
}


class UrlValidator:
    def validate(self, url: str) -> tuple[bool, str]:
        if not url or not url.strip():
            return False, "URL é obrigatória"

        if not self._has_valid_protocol(url):
            return False, "URL inválida"

        if self._is_private_or_blocked(url):
            return False, "URL bloqueada por segurança"

        return True, ""

    def _has_valid_protocol(self, url: str) -> bool:
        for protocol in VALID_PROTOCOLS:
            if url.startswith(protocol):
                return True
        return False

    def _is_private_or_blocked(self, url: str) -> bool:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        if hostname in BLOCKED_HOSTS:
            return True

        return self._is_private_ip(hostname)

    def _is_private_ip(self, hostname: str) -> bool:
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return False
