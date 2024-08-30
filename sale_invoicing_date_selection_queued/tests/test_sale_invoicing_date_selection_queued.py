# © 2024 FactorLibre - Sergio Bustamante <sergio.bustamante@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import TransactionCase


class TestSaleOrderInvoicingQueue(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["sale.advance.payment.inv"]
        cls.queue_obj = cls.env["queue.job"]
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Other partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "service", "invoice_policy": "order"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "price_unit": 20,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.order2 = cls.order.copy({"partner_invoice_id": cls.partner2.id})
        cls.order2.action_confirm()
        cls.order3 = cls.order.copy()
        cls.order3.action_confirm()

    def test_queue_invoicing(self):
        wizard = self.wizard_obj.with_context(
            active_ids=(self.order + self.order2).ids, active_model=self.order._name
        ).create({"invoice_date": "2024-08-04"})
        prev_jobs = self.queue_obj.search([])
        wizard.enqueue_invoices()
        current_jobs = self.queue_obj.search([])
        jobs = current_jobs - prev_jobs
        bridge1 = self.env["sale.order.invoice.date"].search(
            [
                ("sale_order_ids", "in", self.order.ids),
                ("job_ids", "in", self.order.invoicing_job_ids[-1].ids),
            ]
        )
        self.assertTrue(bridge1)
        bridge2 = self.env["sale.order.invoice.date"].search(
            [
                ("sale_order_ids", "in", self.order2.ids),
                ("job_ids", "in", self.order2.invoicing_job_ids[-1].ids),
            ]
        )
        self.assertTrue(bridge2)
        self.assertEqual(len(jobs), 2)
        self.assertTrue(self.order.invoicing_job_ids)
        self.assertTrue(self.order2.invoicing_job_ids)
        self.assertNotEqual(self.order.invoicing_job_ids, self.order2.invoicing_job_ids)
        # Try to enqueue invoicing again
        with self.assertRaises(exceptions.UserError):
            wizard.enqueue_invoices()

    def test_direct_invoices_job(self):
        wizard = self.wizard_obj.with_context(
            active_ids=self.order3.ids, active_model=self.order3._name
        ).create({"invoice_date": "2024-08-04"})
        wizard.enqueue_invoices()
        self.order3.create_invoices_job(True)
        self.assertTrue(self.order3.invoice_ids)
        self.assertEqual(
            self.order3.invoice_ids[0].invoice_date.strftime("%Y-%m-%d"), "2024-08-04"
        )
