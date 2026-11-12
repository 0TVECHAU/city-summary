import unittest
from unittest.mock import MagicMock, patch

import requests

from clients.errors import NotFoundError, ServiceUnavailableError
from clients.http import fetch_json
from processing.preprocessing import preprocess_rate, preprocess_weather


class TestHttpClient(unittest.TestCase):
    @patch("clients.http.time.sleep")
    @patch("clients.http.requests.get")
    def test_retry_on_timeout_then_success(self, mock_get, mock_sleep):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}

        mock_get.side_effect = [
            requests.exceptions.Timeout("timeout 1"),
            mock_response,
        ]

        result = fetch_json("https://example.com")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("clients.http.requests.get")
    def test_404_raises_not_found_without_retry(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(NotFoundError):
            fetch_json("https://example.com/missing")
        self.assertEqual(mock_get.call_count, 1)

    @patch("clients.http.time.sleep")
    @patch("clients.http.requests.get")
    def test_503_exhausts_retries_and_raises_unavailable(self, mock_get, mock_sleep):
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        with self.assertRaises(ServiceUnavailableError):
            fetch_json("https://example.com/down")
        self.assertEqual(mock_get.call_count, 3)


class TestPreprocessing(unittest.TestCase):
    def test_warm_clothes_and_empty_description(self):
        res = preprocess_weather({"temp_c": -5.0, "description": ""})
        self.assertTrue(res["warm_clothes"])
        self.assertEqual(res["description"], "unknown conditions")

    def test_expensive_rate(self):
        res = preprocess_rate("eur", 105.456)
        self.assertEqual(res["currency"], "EUR")
        self.assertEqual(res["rate_to_rub"], 105.46)
        self.assertTrue(res["expensive"])


if __name__ == "__main__":
    unittest.main()
