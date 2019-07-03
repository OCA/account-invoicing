# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date, timedelta

from odoo.tests.common import Form, SingleTransactionCase


class TestCrmOpportunityCurrency(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract1 = cls.env.ref(
            "base_ebill_payment_contract.ebill_payment_contract_demo_1")

    def test_contract_validity(self):
        self.contract1.state = 'open'
        # Contract starting today
        self.contract1.date_start = date.today()
        self.contract1.date_end = date.today() + timedelta(days=10)
        self.assertTrue(self.contract1.is_valid)
        # Contract finishing tomorrow
        self.contract1.date_start = date.today() - timedelta(days=100)
        self.contract1.date_end = date.today()
        self.assertTrue(self.contract1.is_valid)
        # Contract with no end date
        self.contract1.date_start = date.today() - timedelta(days=100)
        self.contract1.date_end = None
        self.assertTrue(self.contract1.is_valid)

    def test_contract_is_not_valid(self):
        self.contract1.state = 'draft'
        self.assertFalse(self.contract1.is_valid)
        self.contract1.state = 'cancel'
        self.assertFalse(self.contract1.is_valid)
        self.contract1.state = 'open'
        # Contract in the past
        self.contract1.date_start = date.today() - timedelta(days=5)
        self.contract1.date_end = date.today() - timedelta(days=1)
        self.assertFalse(self.contract1.is_valid)
        # Contract in the future
        self.contract1.date_start = date.today() + timedelta(days=1)
        self.contract1.date_end = date.today() + timedelta(days=5)
        self.assertFalse(self.contract1.is_valid)
        # Contract in the future with no end date
        self.contract1.date_start = date.today() + timedelta(days=1)
        self.contract1.date_end = None
        self.assertFalse(self.contract1.is_valid)

    def test_contract_canceled(self):
        """Check end date when contract is canceled."""
        self.contract1.date_start = date.today() - timedelta(days=6)
        self.contract1.date_end = date.today() + timedelta(days=6)
        self.contract1.state = 'open'
        with Form(self.contract1) as uiform:
            uiform.state = 'cancel'
        self.assertEqual(date.today(), self.contract1.date_end)
