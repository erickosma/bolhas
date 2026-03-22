"""
Property-based test for URL validation.

**Validates: Requirements 2.1, 2.2, 2.3**
"""

from hypothesis import given, settings, strategies as st

from app import validate_url


@settings(max_examples=200)
@given(s=st.text())
def test_validate_url_consistent_with_http_https_prefix(s: str):
    """
    Propriedade 1: Validação de URL é consistente com prefixo HTTP/HTTPS.

    Para qualquer string s, validate_url(s) retorna válido ⟺
    s não é vazia (após strip) e começa com http:// ou https://.

    **Validates: Requirements 2.1, 2.2, 2.3**
    """
    is_valid, error_msg = validate_url(s)

    should_be_valid = bool(s.strip()) and (
        s.startswith("http://") or s.startswith("https://")
    )

    if should_be_valid:
        assert is_valid is True, f"Expected valid for {s!r}, got error: {error_msg}"
        assert error_msg == ""
    else:
        assert is_valid is False, f"Expected invalid for {s!r}"
        if not s or not s.strip():
            assert error_msg == "URL é obrigatória"
        else:
            assert error_msg == "URL inválida"
