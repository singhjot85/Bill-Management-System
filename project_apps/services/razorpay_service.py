import hmac
import hashlib
import logging
from typing import Any, Dict, Optional
from django.conf import settings
from .base import BaseHTTPService

logger = logging.getLogger(__name__)

class RazorpayService(BaseHTTPService):
    """
    Razorpay specific service layer.
    """
    def __init__(self):
        api_key = settings.RAZORPAY_API_KEY
        api_secret = settings.RAZORPAY_API_SECRETE
        
        if not api_key or not api_secret:
            logger.warning("Razorpay API Key or Secret not configured.")
            
        super().__init__(
            base_url="https://api.razorpay.com/v1",
            auth=(api_key, api_secret)
        )

    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new order in Razorpay.
        Amount should be in major currency unit (e.g. 100.00 for 100 INR).
        """
        payload = {
            "amount": int(amount * 100),  # Razorpay expects amount in smallest currency unit (paise)
            "currency": currency,
            "receipt": receipt,
            "notes": notes or {}
        }
        response = self.post("orders", json=payload)
        response.raise_for_status()
        return response.json()

    def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Fetch details of a specific payment.
        """
        response = self.get(f"payments/{payment_id}")
        response.raise_for_status()
        return response.json()

    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """
        Verify the payment signature sent by Razorpay.
        """
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        secret = settings.RAZORPAY_API_SECRETE
        
        if not secret:
            logger.error("Razorpay API Secret missing during signature verification.")
            return False

        generated_signature = hmac.new(
            secret.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, razorpay_signature)

    def capture_payment(self, payment_id: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
        """
        Capture a payment.
        """
        payload = {
            "amount": int(amount * 100),
            "currency": currency
        }
        response = self.post(f"payments/{payment_id}/capture", json=payload)
        response.raise_for_status()
        return response.json()
