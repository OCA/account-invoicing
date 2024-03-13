# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from datetime import date

from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class InvoiceAutoPostRefCase(AccountTestInvoicingCommon):
    def test_with_ref(self):
        inv1 = self.init_invoice("out_invoice", products=self.product_a)
        prev_invoices = self.env["account.move"].search(domain=[])
        self.assertEqual(inv1.state, "draft")
        inv1.auto_post = "monthly"
        inv1.invoice_date = date(2023, 1, 1)
        inv1.ref = "one"
        inv1.action_post()
        inv2 = self.env["account.move"].search(
            domain=[("id", "not in", prev_invoices.ids)]
        )
        self.assertEqual(inv1.state, "posted")
        self.assertEqual(inv2.ref, "one")
        self.assertEqual(inv2.invoice_date, date(2023, 2, 1))
        self.assertEqual(inv2.state, "draft")
        prev_invoices |= inv2
        inv2.ref = "two"
        inv2.action_post()
        inv3 = self.env["account.move"].search(
            domain=[("id", "not in", prev_invoices.ids)]
        )
        self.assertEqual(inv3.ref, "two")
        self.assertEqual(inv3.invoice_date, date(2023, 3, 1))
        self.assertEqual(inv3.state, "draft")
