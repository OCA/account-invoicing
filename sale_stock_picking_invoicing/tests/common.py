# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.stock_picking_invoicing.tests.common import (
    TestStockPickingInvoicingCommon,
)
from odoo.addons.stock_picking_invoicing.tests.tools import (
    create_with_form_product_product,
)

from .tools import (
    create_with_form_product_combo,
    create_with_form_res_partner,
    create_with_form_sale_order,
)


@tagged("post_install", "-at_install")
class TestSaleStockPickingInvoicingCommon(TestStockPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # In order to avoid errors in the tests CI environment when the tests
        # Create of Invoice by Sale Order using sale.advance.payment.inv object
        # is necessary let default policy as sale_order, just affect demo data.
        # TODO: Is there other form to avoid this problem?
        cls.company.sale_invoicing_policy = "stock_picking"

        # Partner to test Delivery Address
        cls.partner_a_delivery_address = create_with_form_res_partner(
            cls.env,
            {
                "name": "Delivery Address - sale_stock_picking_invoicing",
                "parent_id": cls.partner_a,
                "type": "delivery",
                "category_id": cls.env.ref("base.res_partner_category_14"),
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_br_sp"),
                "zip": "09843-010",
                "country_id": cls.env.ref("base.br"),
                "phone": "+55(11)4545-7777",
                "website": "http://www.company.com",
                "vat": "12345673",
            },
        )

        # Service Product
        cls.product_service = create_with_form_product_product(
            cls.env, cls.common_product_values | {"name": "Service", "type": "service"}
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
