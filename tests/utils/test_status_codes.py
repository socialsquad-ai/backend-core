"""
Unit tests for utils/status_codes.py

Tests verify all status code constants are defined correctly.
"""

from utils import status_codes


class TestStatusCodes:
    """Test cases for status code constants"""

    def test_response_200_code(self):
        """Test RESPONSE_200 constant"""
        assert status_codes.RESPONSE_200 == 200

    def test_response_400_code(self):
        """Test RESPONSE_400 constant"""
        assert status_codes.RESPONSE_400 == 400

    def test_response_404_code(self):
        """Test RESPONSE_404 constant"""
        assert status_codes.RESPONSE_404 == 404

    def test_response_409_code(self):
        """Test RESPONSE_409 constant (conflict)"""
        assert status_codes.RESPONSE_409 == 409

    def test_response_500_code(self):
        """Test RESPONSE_500 constant"""
        assert status_codes.RESPONSE_500 == 500

    def test_all_codes_are_integers(self):
        """Test that all status codes are integers"""
        codes = [
            status_codes.RESPONSE_200,
            status_codes.RESPONSE_400,
            status_codes.RESPONSE_404,
            status_codes.RESPONSE_409,
            status_codes.RESPONSE_500,
        ]
        for code in codes:
            assert isinstance(code, int)

    def test_all_codes_are_valid_http_codes(self):
        """Test that all status codes are valid HTTP status codes"""
        codes = [
            status_codes.RESPONSE_200,
            status_codes.RESPONSE_400,
            status_codes.RESPONSE_404,
            status_codes.RESPONSE_409,
            status_codes.RESPONSE_500,
        ]
        for code in codes:
            assert 100 <= code < 600

    def test_codes_are_defined_as_constants(self):
        """Test that status code constants exist at module level"""
        assert hasattr(status_codes, "RESPONSE_200")
        assert hasattr(status_codes, "RESPONSE_400")
        assert hasattr(status_codes, "RESPONSE_404")
        assert hasattr(status_codes, "RESPONSE_409")
        assert hasattr(status_codes, "RESPONSE_500")

    def test_success_code_is_2xx(self):
        """Test that RESPONSE_200 is in 2xx range"""
        assert 200 <= status_codes.RESPONSE_200 < 300

    def test_client_error_codes_are_4xx(self):
        """Test that 4xx codes are in correct range"""
        client_error_codes = [
            status_codes.RESPONSE_400,
            status_codes.RESPONSE_404,
            status_codes.RESPONSE_409,
        ]
        for code in client_error_codes:
            assert 400 <= code < 500

    def test_server_error_code_is_5xx(self):
        """Test that RESPONSE_500 is in 5xx range"""
        assert 500 <= status_codes.RESPONSE_500 < 600
