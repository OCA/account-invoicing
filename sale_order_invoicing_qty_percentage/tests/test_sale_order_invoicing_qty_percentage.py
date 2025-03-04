# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestSaleOrderInvoicingQtyPercentage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "detailed_type": "service",
                "invoice_policy": "order",
            }
        )
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 20
        cls.order = order_form.save()
        cls.order.action_confirm()
        cls.wizard = (
            cls.env["sale.advance.payment.inv"]
            .with_context(
                active_id=cls.order.id,
                active_ids=cls.order.ids,
                active_model="sale.order",
            )
            .create({"advance_payment_method": "qty_percentage", "qty_percentage": 0.5})
        )

    def test_invoicing_same_data(self):
        self.wizard.create_invoices()
        self.assertEqual(self.order.invoice_ids.invoice_line_ids.quantity, 10)
        self.assertEqual(self.order.order_line.qty_to_invoice, 10)
