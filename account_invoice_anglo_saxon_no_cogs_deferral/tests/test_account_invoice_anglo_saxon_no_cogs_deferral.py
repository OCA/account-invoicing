# Copyright 2023 ForgeFlow S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountAngloSaxonNoCogsDeferral(TransactionCase):
    def setUp(self):
        super(TestAccountAngloSaxonNoCogsDeferral, self).setUp()

        # ENVIRONEMENTS
        self.Invoice = self.env["account.move"]
        self.Account = self.env["account.account"]
        # INSTANCES
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.product1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "standard_price": 5,
            }
        )
        self.product1.product_tmpl_id.valuation = "real_time"
        self.product1.valuation = "real_time"
        self.product1.product_tmpl_id.cost_method = "fifo"
        self.product1.cost_method = "fifo"
        self.stock_input_account = self.Account.create(
            {
                "name": "Stock Input",
                "code": "StockIn",
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
            }
        )
        self.stock_output_account = self.Account.create(
            {
                "name": "COGS",
                "code": "cogs",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.stock_valuation_account = self.Account.create(
            {
                "name": "Stock Valuation",
                "code": "Stock Valuation",
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
        self.stock_journal = self.env["account.journal"].create(
            {
                "name": "Stock Journal",
                "code": "STJTEST",
                "type": "general",
            }
        )
        self.product1.categ_id.write(
            {
                "property_stock_account_input_categ_id": self.stock_input_account.id,
                "property_stock_account_output_categ_id": self.stock_output_account.id,
                "property_stock_valuation_account_id": self.stock_valuation_account.id,
                "property_stock_journal": self.stock_journal.id,
            }
        )

    def test_create_invoice(self):
        # receive 10 units @ 10.00 per unit
        move1 = self.env["stock.move"].create(
            {
                "name": "IN 10 units @ 10.00 per unit",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product1.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
            }
        )
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.qty_done = 10.0
        move1._action_done()
        # create a so
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product1.name,
                            "product_id": self.product1.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": self.product1.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "picking_policy": "direct",
            }
        )
        so.action_confirm()
        # invoice on order
        so._create_invoices()
        pick = so.picking_ids
        pick.action_assign()
        pick.move_lines.write({"quantity_done": 1})
        pick.button_validate()
        self.assertEqual(pick.state, "done")
        invoice = so.invoice_ids
        invoice._post()
        # Check that there's no cogs line involved in the customer invoice
        cogs_line = invoice.mapped("invoice_line_ids").filtered(
            lambda l: l.account_id.code == "cogs"
        )
        self.assertEqual(len(cogs_line), 0)
        # Check that the account move originating from the stock move has a
        # COGS account.
        move = self.env["account.move"].search(
            [("ref", "=", pick.name + " - " + self.product1.name)]
        )
        self.assertEqual(len(move), 1)
        cogs_line = move.mapped("line_ids").filtered(
            lambda l: l.account_id.code == "cogs"
        )
        self.assertEqual(len(cogs_line), 1)
