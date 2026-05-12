import hashlib
import hmac
import unittest
from unittest.mock import MagicMock, patch

from project_apps.services.razorpay_service import RazorpayService


class TestRazorpayService(unittest.TestCase):
    def setUp(self):
        # Patch settings before initializing the service
        self.mock_settings_patcher = patch("project_apps.services.razorpay_service.settings")
        self.mock_settings = self.mock_settings_patcher.start()
        self.mock_settings.RAZORPAY_API_KEY = "test_key"  # pragma: allowlist-secret
        self.mock_settings.RAZORPAY_API_SECRETE = "test_secret"  # pragma: allowlist-secret
        self.service = RazorpayService()

    def tearDown(self):
        self.mock_settings_patcher.stop()

    @patch("requests.Session.request")
    def test_create_order_converts_to_paise(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "order_123"}
        mock_request.return_value = mock_response

        order = self.service.create_order(amount=100.50, receipt="INV-001")

        self.assertEqual(order["id"], "order_123")
        # Verify amount was converted to paise (100.50 * 100 = 10050)
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["json"]["amount"], 10050)
        self.assertEqual(kwargs["json"]["receipt"], "INV-001")

    def test_verify_signature_success(self):
        order_id = "order_123"
        payment_id = "pay_123"
        secret = "test_secret"  # pragma: allowlist-secret

        # Manually generate a valid signature for the test
        msg = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()

        self.mock_settings.RAZORPAY_API_SECRETE = secret

        is_valid = self.service.verify_payment_signature(order_id, payment_id, expected_signature)
        self.assertTrue(is_valid, f"Signature verification failed. Expected {expected_signature}")

    def test_verify_signature_failure(self):
        self.mock_settings.RAZORPAY_API_SECRETE = "test_secret"  # pragma: allowlist-secret
        is_valid = self.service.verify_payment_signature("ord_1", "pay_1", "invalid_sig")
        self.assertFalse(is_valid)
