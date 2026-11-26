# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestPickingInvoicingCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.invoice_model = cls.env["account.move"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Deco Addict",
                "is_company": True,
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "94523",
                "country_id": cls.env.ref("base.us").id,
                "email": "deco_addict@yourcompany.example.com",
                "phone": "(603)-996-3829",
                "website": "http://www.deco-addict.com",
                "vat": "US12345673",
            }
        )
        cls.partner.write(
            {
                "property_payment_term_id": cls.env.ref(
                    "account.account_payment_term_immediate"
                ).id
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Floyd Steward",
                "parent_id": cls.partner.id,
                "function": "Analyst",
                "email": "floyd.steward34@example.com",
                "phone": "(145)-138-3401",
            }
        )
        cls.partner3 = cls.env["res.partner"].create(
            {
                "name": "Lumber Inc",
                "is_company": True,
                "street": "1337 N San Joaquin St",
                "city": "Stockton",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "95202",
                "email": "lumber-inv92@example.com",
                "phone": "(828)-316-0593",
                "country_id": cls.env.ref("base.us").id,
                "website": "http://www.lumber-inc.com",
                "vat": "US12345678",
            }
        )
        cls.partner4 = cls.env["res.partner"].create(
            {
                "name": "Ready Mat",
                "is_company": True,
                "street": "7500 W Linne Road",
                "city": "Tracy",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "95304",
                "email": "ready.mat28@example.com",
                "phone": "(803)-873-6126",
                "country_id": cls.env.ref("base.us").id,
                "website": "http://www.ready-mat.com/",
                "vat": "US12345675",
            }
        )
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Azure Interior",
                "is_company": True,
                "street": "4557 De Silva St",
                "city": "Fremont",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "94538",
                "phone": "(870)-931-0505",
                "country_id": cls.env.ref("base.us").id,
                "email": "azure.Interior24@example.com",
                "website": "http://www.azure-interior.com",
                "vat": "US12345677",
            }
        )
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "A super journal name",
                "code": "ABC",
                "type": "sale",
                "refund_sequence": True,
            }
        )

        cls.product_model = cls.env["product.product"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_account_model = cls.env["account.fiscal.position.account"]
        cls.tax_model = cls.env["account.tax"]
        cls.account_receivable = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                )
            ],
            limit=1,
        )
        cls.account_revenue = cls.env["account.account"].search(
            [("account_type", "=", "expense_direct_cost")], limit=1
        )

        cls.tax_sale_1 = cls.tax_model.create(
            {"name": "Sale tax 20", "type_tax_use": "sale", "amount": "20.00"}
        )
        cls.tax_sale_2 = cls.tax_model.create(
            {"name": "Sale tax 10", "type_tax_use": "sale", "amount": "10.00"}
        )
        cls.tax_purchase_1 = cls.tax_model.create(
            {"name": "Purchase tax 10", "type_tax_use": "purchase", "amount": "10.00"}
        )
        cls.tax_purchase_2 = cls.tax_model.create(
            {"name": "Purchase tax 20", "type_tax_use": "purchase", "amount": "20.00"}
        )

        cls.product_test_1 = cls.product_model.create(
            {
                "name": "Test 1",
                "lst_price": "15000",
                "taxes_id": [(6, 0, [cls.tax_sale_1.id, cls.tax_sale_2.id])],
                "supplier_taxes_id": [
                    (6, 0, [cls.tax_purchase_1.id, cls.tax_purchase_2.id])
                ],
                "property_account_income_id": cls.account_revenue.id,
                "standard_price": "500",
            }
        )
        cls.product_test_2 = cls.product_model.create(
            {
                "name": "Test 2",
                "lst_price": "15000",
                "taxes_id": [(6, 0, [cls.tax_sale_1.id, cls.tax_sale_2.id])],
                "supplier_taxes_id": [
                    (6, 0, [cls.tax_purchase_1.id, cls.tax_purchase_2.id])
                ],
                "property_account_income_id": cls.account_revenue.id,
                "standard_price": "500",
            }
        )
        cls.picking_in = cls.picking_model.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.pick_type_in.id,
                "invoice_state": "2binvoiced",
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )

        # Test PriceList and Sellers Price
        cls.product_category_office = cls.env["product.category"].create(
            {
                "name": "Office Furniture",
            }
        )
        cls.product_price_test = cls.product_model.create(
            {
                "name": "Large Cabinet",
                "categ_id": cls.env["product.category"]
                .create(
                    {
                        "name": "Office Furniture",
                    }
                )
                .id,
                "standard_price": 800.0,
                "list_price": 320.0,
                "type": "consu",
                "weight": 0.330,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "E-COM07",
            }
        )
        cls.price_list = cls.env["product.pricelist"].create({"name": "Test pricelist"})
        cls.price_list.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1234.0,
                "applied_on": "0_product_variant",
                "product_id": cls.product_price_test.id,
            }
        )
        # Data has duplicate line with 2 Prices for same Partner,
        # just remove one for the test.
        # seller_to_delete = cls.product_price_test.seller_ids.filtered(
        #     lambda line: line.price == 785.0
        #     and line.partner_id == cls.env.ref("base.res_partner_4")
        # )
        # seller_to_delete.unlink()

    def _run_picking_onchanges(self, record):
        record._onchange_invoice_state()

    def picking_move_state(self, picking):
        self._run_picking_onchanges(picking)
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.button_validate()

    def create_invoice_wizard(self, pickings):
        wizard_obj = self.env["stock.invoice.onshipping"].with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({"group": "partner_product"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "in", pickings.ids)]
        invoice = self.env["account.move"].search(domain)
        return invoice

    def return_picking_wizard(
        self, picking, invoice_state: str = "2binvoiced"
    ) -> models.Model:
        action = picking.action_return()
        picking_devolution = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(picking_devolution.invoice_state, "none")
        for move in picking_devolution.move_ids:
            self.assertEqual(move.invoice_state, "none")
            move.product_uom_qty = 1
        if invoice_state != "none":
            picking_devolution.invoice_state = invoice_state
            picking_devolution._onchange_invoice_state()
        return picking_devolution

    def create_backorder_wizard(self, picking):
        res_dict_for_back_order = picking.button_validate()
        backorder_wizard = Form(
            self.env[res_dict_for_back_order["res_model"]].with_context(
                **res_dict_for_back_order["context"]
            )
        ).save()
        backorder_wizard.process()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        return backorder
