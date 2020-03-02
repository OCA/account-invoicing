# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceTransmitMethod(TransactionCase):
    def test_create_invoice(self):
        post_method = self.env.ref("account_invoice_transmit_method.post")
        partner1 = self.env["res.partner"].create(
            {
                "is_company": True,
                "name": "Old School Company",
                "customer_invoice_transmit_method_id": post_method.id,
            }
        )
        sale_journal = self.env["account.journal"].create(
            {"code": "XYZZZ", "name": "sale journal (test)", "type": "sale"}
        )
        inv1 = self.env["account.move"].create(
            {
                "partner_id": partner1.id,
                "type": "out_invoice",
                "journal_id": sale_journal.id,
            }
        )
        self.assertEqual(inv1.transmit_method_id, post_method)
