# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, SavepointCase

from ..models.account_move import GROUP_AICT


class TestAccountInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move = cls.env["account.move"]
        # Add current user to group: group_supplier_inv_check_total
        cls.env.ref(GROUP_AICT).write({"users": [(4, cls.env.user.id)]})
        # create a vendor bill
        invoice_form = Form(
            cls.account_move.with_context(default_move_type="in_invoice")
        )
        invoice_form.partner_id = cls.env["res.partner"].create(
            {"name": "test partner"}
        )
        invoice_form.check_total = 1.19
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Test invoice line"
            line_form.price_unit = 2.99
            line_form.tax_ids.clear()
        cls.invoice = invoice_form.save()

    def test_post(self):
        # wrong check_total rise a ValidationError
        self.assertEqual(self.invoice.check_total, 1.19)
        self.assertEqual(self.invoice.check_total_display_difference, -1.80)
        with self.assertRaises(ValidationError):
            self.invoice.post()
