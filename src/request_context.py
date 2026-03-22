from flask import request as flask_request

EXCLUDED_HEADERS = ("host", "content-length", "content-type", "connection")


class RequestContext:
    @staticmethod
    def extract_cookies() -> dict[str, str]:
        return {
            name: value
            for name, value in flask_request.cookies.items()
        }

    @staticmethod
    def extract_headers() -> dict[str, str]:
        return {
            name: value
            for name, value in flask_request.headers
            if name.lower() not in EXCLUDED_HEADERS
        }
