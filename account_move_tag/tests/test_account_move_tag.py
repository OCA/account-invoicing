from psycopg2 import IntegrityError

from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveTag(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tag = cls.env["account.move.tag"]
        cls.tag_card = cls.Tag.create({"name": "Credit Card"})
        cls.tag_deposit = cls.Tag.create({"name": "Deposit"})
        cls.invoice = cls._create_invoice_one_line(price_unit=100.0, post=True)
        cls.bill = cls._create_invoice_one_line(
            move_type="in_invoice", price_unit=50.0, post=True
        )

    def test_default_color(self):
        self.assertTrue(1 <= self.tag_card.color <= 11)

    def test_unique_name(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self.Tag.create({"name": "Credit Card"})

    def test_line_tags_follow_move(self):
        self.invoice.tag_ids = self.tag_card
        self.assertEqual(self.invoice.line_ids.tag_ids, self.tag_card)
        self.assertFalse(self.bill.line_ids.tag_ids)

    def test_search_by_tag(self):
        self.invoice.tag_ids = self.tag_card
        self.bill.tag_ids = self.tag_deposit
        moves = self.env["account.move"].search([("tag_ids", "=", self.tag_card.id)])
        self.assertEqual(moves, self.invoice)
        lines = self.env["account.move.line"].search(
            [("tag_ids", "=", self.tag_deposit.id)]
        )
        self.assertEqual(lines.move_id, self.bill)

    def test_set_tags_in_move_form(self):
        with Form(self.bill) as bill_form:
            bill_form.tag_ids.add(self.tag_deposit)
        self.assertEqual(self.bill.tag_ids, self.tag_deposit)
