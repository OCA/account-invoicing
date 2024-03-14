# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.shipment_advice.tests.common import Common


class TestShipmentAdviceCashOnDelivery(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product COD",
                "type": "product",
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.company = cls.env.ref("base.main_company")
        cls.manual_in = cls.env.ref("account.account_payment_method_manual_in")
        cls.journal_c1 = cls.env["account.journal"].create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
                "bank_acc_number": "123456",
            }
        )

        cls.payment_mode_normal = cls.env.ref(
            "account_payment_mode.payment_mode_inbound_dd1"
        )
        cls.payment_mode_cod = cls.env["account.payment.mode"].create(
            {
                "name": "COD",
                "bank_account_link": "variable",
                "payment_method_id": cls.manual_in.id,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
                "variable_journal_ids": [(6, 0, [cls.journal_c1.id])],
                "cash_on_delivery": True,
            }
        )
        cls.partner_standard = cls.env["res.partner"].create(
            {"name": "partner_standard", "invoicing_mode": "standard"}
        )
        cls.partner_at_shipping = cls.env["res.partner"].create(
            {"name": "partner_at_shipping", "invoicing_mode": "at_shipping"}
        )
        cls.company = cls.env.user.company_id
        cls.default_pricelist = (
            cls.env["product.pricelist"]
            .with_company(cls.company)
            .create(
                {
                    "name": "default_pricelist",
                    "currency_id": cls.company.currency_id.id,
                }
            )
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 3
        )

    def _create_and_process_sale_order(self, dict_val):
        # Create and confirm sale order
        so = self.env["sale.order"].create(dict_val)
        so.action_confirm()
        pick = so.picking_ids

        # Process shipment advice & picking
        shipment_advice = self.env["shipment.advice"].create(
            {"shipment_type": "outgoing"}
        )
        self._plan_records_in_shipment(shipment_advice, pick)
        self._in_progress_shipment_advice(shipment_advice)
        wiz = self._load_records_in_shipment(shipment_advice, pick)
        self.assertEqual(wiz.picking_ids, pick)
        self.assertFalse(wiz.move_line_ids)
        pick.move_ids.write({"quantity_done": 1})
        with trap_jobs() as trap:
            pick._action_done()
            if trap.jobs_count() > 0:
                trap.assert_enqueued_job(
                    pick._invoicing_at_shipping,
                )
                trap.perform_enqueued_jobs()
        shipment_advice.action_done()
        self.assertEqual(shipment_advice.state, "done")

        return pick, shipment_advice

    def _check_picking_shipment(self, pick, shipment, partner):
        self.assertEqual(len(pick.cash_on_delivery_invoice_ids), 1)
        cod_invoice = pick.cash_on_delivery_invoice_ids[0]
        self.assertEqual(cod_invoice.invoice_partner_display_name, partner.name)
        action = shipment.with_context(
            discard_logo_check=True
        ).print_cash_on_delivery_invoices()
        self.assertEqual(action.get("type"), "ir.actions.report")
        self.assertEqual(action.get("report_name"), "account.report_invoice")
        self.assertEqual(action.get("report_type"), "qweb-pdf")
        self.assertEqual(
            action.get("context").get("active_ids"),
            pick.cash_on_delivery_invoice_ids.ids,
        )

    def test01(self):
        """
        Create 1 SO with payment mode cash on delivery for partner without
        invoicing at shipping
        => Should be listed in picking.cash_on_delivery_invoice_ids
        """
        pick, shipment = self._create_and_process_sale_order(
            {
                "partner_id": self.partner_standard.id,
                "partner_invoice_id": self.partner_standard.id,
                "partner_shipping_id": self.partner_standard.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_mode_id": self.payment_mode_cod.id,
            }
        )

        self._check_picking_shipment(pick, shipment, self.partner_standard)

    def test02(self):
        """
        Create 1 SO with payment mode cash on delivery for partner with
        invoicing at shipping
        => Should be listed in picking.cash_on_delivery_invoice_ids
        """
        pick, shipment = self._create_and_process_sale_order(
            {
                "partner_id": self.partner_at_shipping.id,
                "partner_invoice_id": self.partner_at_shipping.id,
                "partner_shipping_id": self.partner_at_shipping.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_mode_id": self.payment_mode_cod.id,
            }
        )

        self._check_picking_shipment(pick, shipment, self.partner_at_shipping)

    def test03(self):
        """
        Create 1 SO without payment mode cash on delivery for partner with
        invoicing at shipping
        => Should NOT be listed in picking.cash_on_delivery_invoice_ids
        """
        pick, dummy = self._create_and_process_sale_order(
            {
                "partner_id": self.partner_at_shipping.id,
                "partner_invoice_id": self.partner_at_shipping.id,
                "partner_shipping_id": self.partner_at_shipping.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_mode_id": self.payment_mode_normal.id,
            }
        )

        self.assertEqual(len(pick.cash_on_delivery_invoice_ids), 0)

    def test04(self):
        """
        Create 1 SO without payment mode cash on delivery for partner without
        invoicing at shipping
        => Should NOT be listed in picking.cash_on_delivery_invoice_ids
        """
        pick, dummy = self._create_and_process_sale_order(
            {
                "partner_id": self.partner_standard.id,
                "partner_invoice_id": self.partner_standard.id,
                "partner_shipping_id": self.partner_standard.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_mode_id": self.payment_mode_normal.id,
            }
        )

        self.assertEqual(len(pick.cash_on_delivery_invoice_ids), 0)
