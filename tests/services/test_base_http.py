import unittest
from unittest.mock import patch, MagicMock
from project_apps.services.base import BaseHTTPService
import requests

class TestBaseHTTPService(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://api.example.com"
        self.service = BaseHTTPService(base_url=self.base_url)

    @patch('requests.Session.request')
    def test_get_request(self, mock_request):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response

        # Call service
        response = self.service.get("test-endpoint")

        # Verify
        mock_request.assert_called_once_with(
            method="GET",
            url=f"{self.base_url}/test-endpoint",
            params=None,
            data=None,
            json=None,
            headers={},
            auth=None,
            timeout=30
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"key": "value"})

    @patch('requests.Session.request')
    def test_post_request_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        payload = {"name": "test"}
        response = self.service.post("create", json=payload)

        mock_request.assert_called_once_with(
            method="POST",
            url=f"{self.base_url}/create",
            params=None,
            data=None,
            json=payload,
            headers={},
            auth=None,
            timeout=30
        )
        self.assertEqual(response.status_code, 201)

    @patch('requests.Session.request')
    def test_custom_headers(self, mock_request):
        service = BaseHTTPService(base_url=self.base_url, headers={"X-Global": "global"})
        mock_response = MagicMock()
        mock_request.return_value = mock_response

        service.get("test", headers={"X-Local": "local"})

        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['headers'], {"X-Global": "global", "X-Local": "local"})

    @patch('requests.Session.request')
    def test_request_exception(self, mock_request):
        mock_request.side_effect = requests.exceptions.RequestException("Error")
        
        with self.assertRaises(requests.exceptions.RequestException):
            self.service.get("error")
