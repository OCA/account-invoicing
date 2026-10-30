# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.stock_picking_invoicing.tests.common import (
    TestPickingInvoicingCommon,
)

from .tools import (
    create_with_form_product_combo,
    create_with_form_sale_order,
)


@tagged("post_install", "-at_install")
class TestSaleStockPickingInvoicingCommon(TestPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company

        cls.partner_a = cls.env["res.partner"].create(
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
        cls.partner_a.write(
            {
                "property_payment_term_id": cls.env.ref(
                    "account.account_payment_term_immediate"
                ).id,
            }
        )
        cls.partner_category = cls.env["res.partner.category"].create(
            {"name": "Migration Test Category"}
        )

        cls.tax_model = cls.env["account.tax"]
        cls.tax_sale_1 = cls.tax_model.create(
            {"name": "Sale tax 20", "type_tax_use": "sale", "amount": 20.0}
        )
        cls.tax_sale_2 = cls.tax_model.create(
            {"name": "Sale tax 10", "type_tax_use": "sale", "amount": 10.0}
        )
        cls.tax_purchase_1 = cls.tax_model.create(
            {"name": "Purchase tax 10", "type_tax_use": "purchase", "amount": 10.0}
        )
        cls.tax_purchase_2 = cls.tax_model.create(
            {"name": "Purchase tax 20", "type_tax_use": "purchase", "amount": 20.0}
        )
        cls.account_revenue = cls.env["account.account"].search(
            [("account_type", "=", "expense_direct_cost")], limit=1
        )

        cls.common_product_values = {
            "lst_price": 15000.0,
            "taxes_id": [Command.set((cls.tax_sale_1 + cls.tax_sale_2).ids)],
            "supplier_taxes_id": [
                Command.set((cls.tax_purchase_1 + cls.tax_purchase_2).ids)
            ],
            "property_account_income_id": cls.account_revenue.id,
            "standard_price": 500.0,
            "is_storable": True,
            "invoice_policy": "order",
        }
        cls.product_storable_1 = cls.env["product.product"].create(
            cls.common_product_values | {"name": "Test 1", "type": "consu"}
        )
        cls.product_storable_2 = cls.env["product.product"].create(
            cls.common_product_values | {"name": "Test 2", "type": "consu"}
        )

        cls.picking_out_1 = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner_a.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )
        cls.env["stock.move"].create(
            {
                "product_id": cls.product_storable_1.id,
                "picking_id": cls.picking_out_1.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "product_uom_qty": 1.0,
                "product_uom": cls.product_storable_1.uom_id.id,
            }
        )

        # In order to avoid errors in the tests CI environment when the tests
        # Create of Invoice by Sale Order using sale.advance.payment.inv object
        # is necessary let default policy as sale_order, just affect demo data.
        # TODO: Is there other form to avoid this problem?
        cls.company.sale_invoicing_policy = "stock_picking"

        # Partner to test Delivery Address
        cls.partner_a_delivery_address = cls.env["res.partner"].create(
            {
                "name": "Delivery Address - sale_stock_picking_invoicing",
                "parent_id": cls.partner_a.id,
                "type": "delivery",
                "category_id": [Command.set(cls.partner_category.ids)],
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "09843-010",
                "country_id": cls.env.ref("base.us").id,
                "phone": "+55(11)4545-7777",
                "website": "http://www.company.com",
                "vat": "12345673",
            }
        )

        # Service Product
        cls.product_service = cls.env["product.product"].create(
            cls.common_product_values
            | {
                "name": "Service",
                "type": "service",
                "is_storable": False,
            }
        )

        # Common Sale Order Data
        cls.pricelist = cls.env["product.pricelist"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        incoterm_fob = cls.env["account.incoterms"].search(
            [("active", "=", True), ("name", "=", "FREE ON BOARD")]
        )

        cls.so_vals = {
            "partner_id": cls.partner_a,
            "partner_invoice_id": cls.partner_a,
            "partner_shipping_id": cls.partner_a,
            "pricelist_id": cls.pricelist,
            "company_id": cls.company,
            "client_order_ref": "Customer Ref Test",
            "incoterm": incoterm_fob,
            "note": "Test Note sale_stock_picking_invoicing",
        }

        cls.so_vals_delivery_partner = cls.so_vals | {
            "partner_shipping_id": cls.partner_a_delivery_address,
        }

        cls.so_line_product_1 = [
            {
                "product_id": cls.product_storable_1,
                "product_uom_qty": 1.0,
            }
        ]

        cls.so_line_product_2 = [
            {
                "product_id": cls.product_storable_2,
                "product_uom_qty": 2.0,
            }
        ]

        cls.so_line_product_service = [
            {
                "product_id": cls.product_service,
                "product_uom_qty": 2.0,
            }
        ]

        cls.so_line_note = [
            {
                "name": "This is a Note",
                "display_type": "line_note",
            }
        ]

        cls.so_line_section = [
            {
                "name": "This is a Section",
                "display_type": "line_section",
            }
        ]

        # Sale Orders
        cls.sale_order_0 = create_with_form_sale_order(
            cls.env, cls.so_vals, cls.so_line_product_1
        )

        cls.sale_order_1 = create_with_form_sale_order(
            cls.env,
            cls.so_vals_delivery_partner,
            cls.so_line_product_1
            + cls.so_line_note
            + cls.so_line_section
            + cls.so_line_product_2,
        )

        cls.sale_order_2 = create_with_form_sale_order(
            cls.env,
            cls.so_vals_delivery_partner,
            cls.so_line_product_1
            + cls.so_line_note
            + cls.so_line_section
            + cls.so_line_product_service,
        )

        cls.sale_order_3 = create_with_form_sale_order(
            cls.env,
            cls.so_vals,
            cls.so_line_product_1
            + cls.so_line_note
            + cls.so_line_section
            + cls.so_line_product_2,
        )

        cls.sale_order_4 = create_with_form_sale_order(
            cls.env,
            cls.so_vals,
            cls.so_line_product_1
            + cls.so_line_note
            + cls.so_line_section
            + cls.so_line_product_2,
        )

        # Combo Case
        cls.combo_service = create_with_form_product_combo(
            cls.env,
            {"name": "Service Choice"},
            [{"product_id": cls.product_service}],
        )

        cls.combo_consu_1 = create_with_form_product_combo(
            cls.env,
            {"name": "Consu Choice 1"},
            [{"product_id": cls.product_storable_1}],
        )

        cls.combo_consu_2 = create_with_form_product_combo(
            cls.env,
            {"name": "Consu Choice 2"},
            [{"product_id": cls.product_storable_2}],
        )

        # Combo product uses direct .create() instead of Form because
        # combo products require linking combo_ids via Command.link which
        # is not easily handled through the Form helper.
        cls.product_combo = cls.env["product.product"].create(
            {
                "name": "Test Meal Combo",
                "type": "combo",
                "list_price": 75.0,
                "combo_ids": [
                    Command.link(cls.combo_service.id),
                    Command.link(cls.combo_consu_1.id),
                    Command.link(cls.combo_consu_2.id),
                ],
            }
        )

        cls.sale_order_5 = create_with_form_sale_order(
            cls.env,
            cls.so_vals_delivery_partner,
            [
                {"product_id": cls.product_combo, "product_uom_qty": 1.0},
            ],
        )
        cls.sale_order_5.order_line = [
            Command.create(
                {
                    "product_id": product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": product.list_price,
                    "combo_item_id": combo.combo_item_ids.id,
                    "linked_line_id": cls.sale_order_5.order_line.id,
                }
            )
            for product, combo in (
                (cls.product_service, cls.combo_service),
                (cls.product_storable_1, cls.combo_consu_1),
                (cls.product_storable_2, cls.combo_consu_2),
            )
        ]

    def run_sale_picking_process(self, sale_order):
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        self.picking_move_state(picking)
        return picking
