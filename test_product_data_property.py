"""
Property-based tests for Dados_Produto structure and JSON round-trip.

**Validates: Requirements 4.4, 4.5, 5.3**
"""

import json

from hypothesis import given, settings, strategies as st

EXPECTED_KEYS = {"title", "price", "description"}


# --- Propriedade 2 ---

@settings(max_examples=200)
@given(
    title=st.text(),
    price=st.text(),
    description=st.text(),
)
def test_product_data_structure_is_consistent(title: str, price: str, description: str):
    """
    Propriedade 2: Estrutura do Dados_Produto é consistente.

    Para qualquer dicionário com chaves title, price, description e valores string,
    o dicionário deve conter exatamente as chaves esperadas com valores do tipo str.

    **Validates: Requirements 4.4, 4.5**
    """
    dados_produto = {
        "title": title,
        "price": price,
        "description": description,
    }

    # Deve conter exatamente as chaves esperadas
    assert set(dados_produto.keys()) == EXPECTED_KEYS, (
        f"Chaves inesperadas: {set(dados_produto.keys())} != {EXPECTED_KEYS}"
    )

    # Todos os valores devem ser do tipo str
    for key in EXPECTED_KEYS:
        assert isinstance(dados_produto[key], str), (
            f"Valor de '{key}' não é str: {type(dados_produto[key])}"
        )


# --- Propriedade 3 ---

@settings(max_examples=200)
@given(
    title=st.text(),
    price=st.text(),
    description=st.text(),
)
def test_product_data_json_round_trip(title: str, price: str, description: str):
    """
    Propriedade 3: Round-trip de serialização JSON do Dados_Produto.

    Para qualquer dicionário Dados_Produto válido, serializar com json.dumps
    e deserializar com json.loads deve produzir um dicionário equivalente ao original.

    **Validates: Requirement 5.3**
    """
    dados_produto = {
        "title": title,
        "price": price,
        "description": description,
    }

    serialized = json.dumps(dados_produto)
    deserialized = json.loads(serialized)

    assert deserialized == dados_produto, (
        f"Round-trip falhou: {deserialized} != {dados_produto}"
    )
