import logging
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, ViewportSize

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)


class BrowserSession:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def start(
        self,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        target_url: str = "",
    ):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)

        user_agent, extra_headers = self._resolve_headers(headers)

        self._context = self._browser.new_context(
            user_agent=user_agent,
            viewport=ViewportSize(width=1920, height=1080),
            extra_http_headers=extra_headers if extra_headers else None,
        )

        if cookies:
            self._inject_cookies(cookies, target_url)

        self._page = self._context.new_page()
        return self._page

    def close(self):
        resources = [
            (self._page, "page"),
            (self._context, "context"),
            (self._browser, "browser"),
        ]
        for resource, name in resources:
            self._close_resource(resource, name)
        self._stop_playwright()

    def _resolve_headers(self, headers: dict[str, str] | None) -> tuple[str, dict]:
        if not headers:
            return DEFAULT_USER_AGENT, {}

        extra_headers = dict(headers)
        user_agent = extra_headers.pop(
            "User-Agent",
            extra_headers.pop("user-agent", DEFAULT_USER_AGENT),
        )
        return user_agent, extra_headers

    def _inject_cookies(self, cookies: dict[str, str], target_url: str):
        parsed = urlparse(target_url)
        domain = parsed.hostname or ""
        is_secure = target_url.startswith("https")

        playwright_cookies: list[dict] = [
            {
                "name": cookie_name,
                "value": cookie_value,
                "domain": domain,
                "path": "/",
                "httpOnly": False,
                "secure": is_secure,
                "sameSite": "Lax",
            }
            for cookie_name, cookie_value in cookies.items()
        ]
        self._context.add_cookies(playwright_cookies)  # type: ignore[arg-type]
        logger.debug("Injetados %d cookies para domínio %s", len(playwright_cookies), domain)

    def _close_resource(self, resource, name: str):
        if not resource:
            return
        try:
            resource.close()
        except Exception as error:
            logger.warning("Erro ao fechar %s: %s", name, error)

    def _stop_playwright(self):
        if not self._playwright:
            return
        try:
            self._playwright.stop()
        except Exception as error:
            logger.warning("Erro ao encerrar Playwright: %s", error)
