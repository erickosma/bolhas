import logging
from flask import Flask, render_template, request

from crawler import get_product_data

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_url(url: str) -> tuple[bool, str]:
    """
    Valida a URL fornecida.
    Retorna (True, "") se válida, ou (False, mensagem_erro) se inválida.
    """
    if not url or not url.strip():
        return False, "URL é obrigatória"
    if not url.startswith("http://") and not url.startswith("https://"):
        return False, "URL inválida"
    return True, ""


@app.route("/")
def index():
    """Renderiza index.html com o formulário."""
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Recebe URL via form POST.
    Valida a URL.
    Chama get_product_data(url).
    Renderiza result.html com dados ou erro.
    """
    url = request.form.get("url", "")
    logger.info("Requisição POST /scrape recebida com URL: %s", url)

    is_valid, error_msg = validate_url(url)
    if not is_valid:
        logger.info("URL inválida: %s - %s", url, error_msg)
        return render_template("index.html", error=error_msg)

    logger.info("URL válida, iniciando crawler para: %s", url)
    result = get_product_data(url)

    if "error" in result:
        logger.error("Crawler retornou erro para URL %s: %s", url, result["error"])
        return render_template("result.html", error=result["error"])

    logger.info("Dados extraídos com sucesso para URL: %s", url)
    return render_template("result.html", product=result)


if __name__ == "__main__":
    app.run(debug=True)
