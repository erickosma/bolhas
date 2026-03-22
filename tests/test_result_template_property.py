"""
Property-based tests for result.html template rendering.

**Validates: Requirements 6.4, 8.1**
"""

from markupsafe import escape

from hypothesis import given, settings, strategies as st

from src.app import app


# --- Propriedade 4 ---

@settings(max_examples=200)
@given(error_msg=st.text(min_size=1))
def test_error_messages_displayed_in_result_page(error_msg: str):
    """
    Propriedade 4: Mensagens de erro são exibidas na página de resultado.

    Para qualquer string de erro não vazia, ao renderizar result.html
    com {"error": mensagem}, o HTML resultante deve conter a mensagem de erro.

    **Validates: Requirement 6.4**
    """
    with app.app_context():
        with app.test_request_context():
            html = app.jinja_env.get_template("result.html").render(error=error_msg)
            escaped = str(escape(error_msg))
            assert escaped in html, (
                f"Mensagem de erro não encontrada no HTML: {error_msg!r}"
            )


# --- Propriedade 5 ---

@settings(max_examples=200)
@given(
    title=st.text(min_size=1, alphabet=st.characters(blacklist_categories=("Cs",))),
    price=st.text(min_size=1, alphabet=st.characters(blacklist_categories=("Cs",))),
    description=st.text(min_size=1, alphabet=st.characters(blacklist_categories=("Cs",))),
)
def test_product_data_displayed_in_result_page(title: str, price: str, description: str):
    """
    Propriedade 5: Dados do produto são exibidos na página de resultado.

    Para qualquer Dados_Produto com valores não vazios, ao renderizar result.html,
    o HTML resultante deve conter título, preço e descrição.

    **Validates: Requirement 8.1**
    """
    product = {"title": title, "price": price, "description": description}
    with app.app_context():
        with app.test_request_context():
            html = app.jinja_env.get_template("result.html").render(product=product)
            assert str(escape(title)) in html, f"Título não encontrado no HTML: {title!r}"
            assert str(escape(price)) in html, f"Preço não encontrado no HTML: {price!r}"
            assert str(escape(description)) in html, f"Descrição não encontrada no HTML: {description!r}"
