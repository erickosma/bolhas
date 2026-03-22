from src.url_validator import UrlValidator


class TestUrlValidatorEmptyInput:
    def test_empty_string_is_invalid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("")
        assert is_valid is False
        assert message == "URL é obrigatória"

    def test_whitespace_only_is_invalid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("   ")
        assert is_valid is False
        assert message == "URL é obrigatória"

    def test_none_like_empty_is_invalid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("\t\n")
        assert is_valid is False
        assert message == "URL é obrigatória"


class TestUrlValidatorProtocol:
    def test_no_protocol_is_invalid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("example.com")
        assert is_valid is False
        assert message == "URL inválida"

    def test_ftp_protocol_is_invalid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("ftp://example.com")
        assert is_valid is False
        assert message == "URL inválida"

    def test_http_is_valid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://example.com")
        assert is_valid is True
        assert message == ""

    def test_https_is_valid(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("https://example.com/product")
        assert is_valid is True
        assert message == ""


class TestUrlValidatorSsrfProtection:
    def test_blocks_localhost(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://localhost/admin")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_127_0_0_1(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://127.0.0.1:8080/secret")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_zero_address(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://0.0.0.0/")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_metadata_endpoint(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://metadata.google.internal/computeMetadata")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_aws_metadata_ip(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://169.254.169.254/latest/meta-data")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_private_ip_10_range(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://10.0.0.1/internal")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_blocks_private_ip_192_168_range(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("http://192.168.1.1/router")
        assert is_valid is False
        assert message == "URL bloqueada por segurança"

    def test_allows_public_url(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("https://www.amazon.com.br/product")
        assert is_valid is True
        assert message == ""

    def test_allows_public_ip(self):
        validator = UrlValidator()
        is_valid, message = validator.validate("https://8.8.8.8/")
        assert is_valid is True
        assert message == ""
