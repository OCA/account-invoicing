from odoo.tests import Form, TransactionCase


class TestPortalInvoiceSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Move = cls.env["account.move"]
        cls.partner = cls.env["res.partner"].create({"name": "Portal Search Partner"})

        # Invoice 1
        f1 = Form(cls.Move.with_context(default_move_type="out_invoice"))
        f1.partner_id = cls.partner
        f1.payment_reference = "PORTAL-AAA"
        with f1.invoice_line_ids.new() as l1:
            l1.name = "Line 1"
            l1.quantity = 1
            l1.price_unit = 10
        cls.inv1 = f1.save()

        # Invoice 2
        f2 = Form(cls.Move.with_context(default_move_type="out_invoice"))
        f2.partner_id = cls.partner
        f2.payment_reference = "PORTAL-BBB"
        with f2.invoice_line_ids.new() as l2:
            l2.name = "Line 2"
            l2.quantity = 1
            l2.price_unit = 10
        cls.inv2 = f2.save()

    def test_search_uses_portal_invoice_filter_context(self):
        # Keep the base domain narrow so we only test your AND() logic
        base_domain = [("id", "in", (self.inv1.id, self.inv2.id))]

        res = self.env["account.move"].with_context(
            portal_invoice_filter="PORTAL-AAA"
        ).search(base_domain)

        self.assertIn(self.inv1, res)
        self.assertNotIn(self.inv2, res)
