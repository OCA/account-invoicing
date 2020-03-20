# Copyright 2016 Davide Corio - davidecorio.com
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountForceNumber(TransactionCase):
    def test_force_number(self):
        # in order to test the correct assignment of the internal_number
        # I create a customer invoice.
        invoice_vals = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_3").id,
                    "quantity": 1.0,
                    "account_id": self.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "[PCSC234] PC Assemble SC234",
                    "price_unit": 450.00,
                },
            )
        ]
        invoice = self.env["account.move"].create(
            {
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "partner_id": self.env.ref("base.res_partner_12").id,
                "type": "out_invoice",
                "invoice_line_ids": invoice_vals,
            }
        )
        # I set the force number
        invoice.write({"move_name": "0001"})
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
        invoice_2 = self.env["account.move"].create(
            {
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "partner_id": self.env.ref("base.res_partner_12").id,
                "type": "out_invoice",
                "invoice_line_ids": invoice_vals,
            }
        )
        invoice_2.unlink()
