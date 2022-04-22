# Copyright 2016 Davide Corio - davidecorio.com
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountForceNumber(AccountTestInvoicingCommon):
    def create_invoice(self, move_name=None):
        partner_id = self.env.ref("base.res_partner_12").id
        invoice_vals = {
            "move_type": "out_invoice",
            "partner_id": partner_id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Test product",
                        "quantity": 1,
                        "price_unit": 450,
                        "tax_ids": [(6, 0, [])],
                    },
                )
            ],
        }
        invoice = (
            self.env["account.move"]
            .with_context(default_move_type="out_invoice")
            .create(invoice_vals)
        )
        if move_name:
            invoice.write({"move_name": "0001"})
        return invoice

    def test_force_number(self):
        # in order to test the correct assignment of the internal_number
        # I create a customer invoice.
        # I set the force number
        invoice = self.create_invoice(move_name="0001")
        # I validate the invoice
        invoice.action_post()
        # I check that the invoice number is the one we expect
        self.assertEqual(invoice.name, invoice.move_name, msg="Wrong number")
        # I check move_name is not modified when validating the invoice.
        self.assertEqual(invoice.name, "0001")
        # Delete invoice while move_name is True
        with self.assertRaises(UserError):
            invoice.unlink()
        # Delete invoice while move_name is False
        invoice_2 = self.create_invoice()
        invoice_2.unlink()
