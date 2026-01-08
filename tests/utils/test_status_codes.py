from utils import status_codes


class TestStatusCodes:
    def test_response_200_constant(self):
        assert status_codes.RESPONSE_200 == 200

    def test_response_404_constant(self):
        assert status_codes.RESPONSE_404 == 404

    def test_response_400_constant(self):
        assert status_codes.RESPONSE_400 == 400

    def test_response_409_constant(self):
        assert status_codes.RESPONSE_409 == 409

    def test_response_500_constant(self):
        assert status_codes.RESPONSE_500 == 500

    def test_all_status_codes_are_integers(self):
        assert isinstance(status_codes.RESPONSE_200, int)
        assert isinstance(status_codes.RESPONSE_404, int)
        assert isinstance(status_codes.RESPONSE_400, int)
        assert isinstance(status_codes.RESPONSE_409, int)
        assert isinstance(status_codes.RESPONSE_500, int)

    def test_all_status_codes_are_valid_http_codes(self):
        assert 100 <= status_codes.RESPONSE_200 < 600
        assert 100 <= status_codes.RESPONSE_404 < 600
        assert 100 <= status_codes.RESPONSE_400 < 600
        assert 100 <= status_codes.RESPONSE_409 < 600
        assert 100 <= status_codes.RESPONSE_500 < 600

    def test_status_codes_match_http_standard(self):
        # 2xx success
        assert 200 <= status_codes.RESPONSE_200 < 300
        # 4xx client errors
        assert 400 <= status_codes.RESPONSE_404 < 500
        assert 400 <= status_codes.RESPONSE_400 < 500
        assert 400 <= status_codes.RESPONSE_409 < 500
        # 5xx server errors
        assert 500 <= status_codes.RESPONSE_500 < 600
