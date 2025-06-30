# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.payment.tests.common import PaymentCommon


class TestReference(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )

    def test_invoice_on_transaction_done(self):
        """Test invoice payment reference is the transaction reference."""
        reference = "TESTREF001"
        tx = self._create_transaction(
            flow="direct",
            state="pending",
            sale_order_ids=[self.sale_order.id],
            reference=reference,
        )
        self.assertEqual(tx.reference, reference)
        tx._set_done()
        tx.operation = "validation"
        tx._post_process()
        tx._invoice_sale_orders()
        self.assertTrue(tx.invoice_ids)
        tx.invoice_ids.filtered(lambda inv: inv.state == "draft").action_post()
        self.assertEqual(tx.invoice_ids.payment_reference, reference)
