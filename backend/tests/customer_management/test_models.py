import pytest

from tests.factories import CustomerFactory


@pytest.mark.django_db
class TestCustomer:

    def setup_method(self):
        self.customer = CustomerFactory()

    def test_customer_saves(self):
        self.customer.refresh_from_db()
        # print(">>>> ", self.customer.id)
        # print(">>>> ", self.customer.pk)
