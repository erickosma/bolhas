import logging
import os

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect

from src.crawler import get_product_data
from src.url_validator import UrlValidator
from src.request_context import RequestContext

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32).hex())

csrf = CSRFProtect(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

url_validator = UrlValidator()
request_context = RequestContext()


def validate_url(url: str) -> tuple[bool, str]:
    return url_validator.validate(url)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.form.get("url", "")
    sanitized_url = url.replace("\n", "").replace("\r", "")
    logger.info("POST /scrape recebida com URL: %s", sanitized_url)

    is_valid, error_message = validate_url(url)
    if not is_valid:
        return render_template("index.html", error=error_message)

    user_cookies = request_context.extract_cookies()
    user_headers = request_context.extract_headers()

    result = get_product_data(
        url,
        cookies=user_cookies,
        headers=user_headers,
    )

    if "error" in result:
        return render_template("result.html", error=result["error"])

    return render_template("result.html", product=result)


if __name__ == "__main__":
    app.run(debug=True)
