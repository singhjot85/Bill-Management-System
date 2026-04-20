from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class OrderInterfaceChoices(TextChoices):

    CREATE_PAYMENT = "create-payment", _("Create a payment")
    CREATE_ORDER = "create-order", _("Create an Order")

    CAPTURE_PAYMENT = "capture-payment", _("Capture Payment")
    UPDATE_PAYMENT = "update-payment", _("Update a Payment")
    FETCH_PAYMENT = "fetch-payment", _("Fetch a Single Payment")
    FETCH_ALL_PAYMENT = "fetch-all-payment", _("Fetch All Payments")


class OrderStateChoices(TextChoices):
    CREATED = "created", _("Created")
    ATTEMPTED = "attempted", _("Attempted/ Under - processing")
    PAID = "paid", _("Paid")


class PaymentStateChoices(TextChoices):
    CREATED = "created", _("Created")
    AUTHORIZED = "authorized", _("Authorized")
    FAILED = "failed", _("Authorized but Failed")
    CAPTURED = "captured", _("Captured")


class CurrencyChoices(TextChoices):
    INR = "INR", _("Indian National Rupee")
    USD = "USD", _("United State Dollar")
    YEN = "YEN", _("Chinese Yen")


class PaymentModeChoices(TextChoices):
    UPI = "upi", _("UPI")
    EMI = "emi", _("EMI")
    CARD = "card", _("Card")
    WALLET = "wallet", _("E- Wallet")
    PAYLATER = "paylater", _("Paylater")
    CARDLESS_EMI = "cardless_emi", _("Cardless Emi")
    INTERNET_BANKING = "netbanking", _("Internet Banking")


class CardNetworkChoices(TextChoices):
    VISA = "visa", _("Visa")
    BAJAJ = "bajaj", _("Bajaj")
    RUPAY = "rupay", _("Rupay")
    DINERS = "diners", _("Diners")
    MAESTRO = "maestro", _("Maestro")
    AMEX = "amex", _("American Express")
    MASTERCARD = "mastercard", _("Mastercard")


class CardlessEMIProviderChoices(TextChoices):
    IDFB = "idfb", _("IDFC Bank")
    HDFC = "hdfc", _("HDFC Bank")
    AXIOS = "axio", _("walnut369")
    ICIC = "icic", _("ICICI Bank")
    KKKBK = "kkbk", _("Kotak Bank")
    FIBE = "earlysalary", _("Fibe")
    ZESTMONEY = "zestmoney", _("ZestMoney")


PAYMENTS_TYPE_CHOICE_TO_MODEL_MAP = {
    "upi": "UPIDetails",
    "emi": "EMIDetails",
    "card": "CardDetails",
    "wallet": "WalletDetails",
    "paylater": "PayLaterDetails",
    "cardless_emi": "CardlessEMIDetails",
    "netbanking": "InternetBankingDetails",
}
