# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import Form, tagged

from odoo.addons.stock_picking_invoicing.tests.common import (
    TestStockPickingInvoicingCommon,
)
from odoo.addons.stock_picking_invoicing.tests.tools import (
    create_with_form_pck_backorder,
    create_with_form_product_product,
)

from .tools import (
    create_with_form_product_combo,
    create_with_form_sale_adv_pay_inv,
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
        cls.company.sale_invoicing_policy = "stock_picking"

        # The groups they grant are required to write the partner
        # invoice/shipping address and the pricelist of the Sale Order Form.
        cls.env.user.groups_id |= cls.env.ref(
            "account.group_delivery_invoice_address"
        ) | cls.env.ref("product.group_product_pricelist")

        # Partner to test Delivery Address
        cls.partner_stock_1_delivery_address = cls.env["res.partner"].create(
            {
                "name": "Client Delivery Address - sale_stock_picking_invoicing",
                "country_id": cls.env.ref("base.be").id,
                "state_id": cls.env.ref("base.state_be_2").id,
                "zip": "1234",
                "street": "Rua B",
                # Contact Information
                "company_type": "person",
                "type": "delivery",
                "parent_id": cls.partner_stock_1.id,
            }
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
            "partner_id": cls.partner_stock_1,
            "partner_invoice_id": cls.partner_stock_1,
            "partner_shipping_id": cls.partner_stock_1,
            "pricelist_id": cls.pricelist,
            "company_id": cls.company,
            "client_order_ref": "Customer Ref Test",
            "incoterm": incoterm_fob,
            "note": "Test Note sale_stock_picking_invoicing",
        }

        cls.so_vals_delivery_partner = cls.so_vals | {
            "partner_shipping_id": cls.partner_stock_1_delivery_address,
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
                "name": "This is a Note 1",
                "display_type": "line_note",
            }
        ]

        cls.so_line_note_2 = [
            {
                "name": "This is a Note 2",
                "display_type": "line_note",
            }
        ]

        cls.so_line_note_3 = [
            {
                "name": "This is a Note 3",
                "display_type": "line_note",
            }
        ]

        cls.so_line_note_4 = [
            {
                "name": "This is a Note 4",
                "display_type": "line_note",
            }
        ]

        cls.so_line_section = [
            {
                "name": "This is a Section 1",
                "display_type": "line_section",
            }
        ]

        cls.so_line_section_2 = [
            {
                "name": "This is a Section 2",
                "display_type": "line_section",
            }
        ]

        cls.so_line_section_3 = [
            {
                "name": "This is a Section 3",
                "display_type": "line_section",
            }
        ]

        cls.so_line_section_4 = [
            {
                "name": "This is a Section 4",
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
            + cls.so_line_note_2
            + cls.so_line_section_2
            + cls.so_line_product_service,
        )

        cls.sale_order_3 = create_with_form_sale_order(
            cls.env,
            cls.so_vals,
            cls.so_line_product_1
            + cls.so_line_note_3
            + cls.so_line_section_3
            + cls.so_line_product_2,
        )

        cls.sale_order_4 = create_with_form_sale_order(
            cls.env,
            cls.so_vals,
            cls.so_line_product_1
            + cls.so_line_note_4
            + cls.so_line_section_4
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

        # Case Products Consu Not Storable
        cls.product_consu_not_storable_1 = create_with_form_product_product(
            cls.env,
            cls.common_product_values
            | {
                "name": "Consu Not Storable",
                "type": "consu",
                "is_storable": False,
                "invoice_policy": "delivery",
            },
        )

        cls.product_consu_not_storable_2 = create_with_form_product_product(
            cls.env,
            cls.common_product_values
            | {
                "name": "Consu Not Storable",
                "type": "consu",
                "is_storable": False,
                "invoice_policy": "delivery",
            },
        )

        cls.so_line_product_consu_not_storable_1 = [
            {
                "product_id": cls.product_consu_not_storable_1,
                "product_uom_qty": 2.0,
            }
        ]

        cls.so_line_product_consu_not_storable_2 = [
            {
                "product_id": cls.product_consu_not_storable_2,
                "product_uom_qty": 2.0,
            }
        ]
        cls.sale_order_6 = create_with_form_sale_order(
            cls.env,
            cls.so_vals_delivery_partner,
            cls.so_line_product_consu_not_storable_1
            + cls.so_line_product_consu_not_storable_2,
        )

    def run_sale_picking_process(self, sale_order):
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        self.picking_move_state(picking)
        return picking

    def _create_confirmed_sale_order(
        self, qty=1.0, invoice_policy="order", product=None, policy="both"
    ):
        """Create a confirmed Sale Order (and its Picking) for the tests."""
        self.company.sale_invoicing_policy = policy
        product = product or self.product_storable_1
        product.invoice_policy = invoice_policy
        sale_order = create_with_form_sale_order(
            self.env,
            self.so_vals,
            [{"product_id": product, "product_uom_qty": qty}],
        )
        sale_order.action_confirm()
        return sale_order

    def _check_values_from_sale(self, record, sale_values, not_used, message):
        """Check that ``record`` has the values coming from the Sale dict."""
        for field, value in sale_values.items():
            if field in not_used or field not in record._fields:
                continue
            if isinstance(value, list | tuple):
                # x2many fields are Commands, they are not compared
                continue
            field_obj = record._fields[field]
            if field_obj.type == "many2one":
                self.assertEqual(
                    record[field].id or False, value or False, message % field
                )
            else:
                # The value from the Sale dict is not always in the cache
                # format of the field (e.g. a datetime for a date field)
                expected = field_obj.convert_to_cache(value, record)
                self.assertEqual(
                    record[field] or False, expected or False, message % field
                )

    def _invoice_from_picking_with_advance(self, deduct_down_payments):
        """Invoice a done Picking of a Sale Order fully paid in advance.

        The Sale Order is paid in advance (100% of the 10 ordered units) and
        delivered only in part (4 units, with a backorder for the rest), so the
        deduction of the Down Payments is worth more than the quantity invoiced
        from the Picking: the created Invoice has a negative total, which is
        the only case where the 'deduct_down_payments' option changes the
        result (see the wizard `_create_invoice`).
        """
        sale_order = self._create_confirmed_sale_order(
            qty=10.0, invoice_policy="delivery", product=self.product_storable_1
        )
        down_payments = create_with_form_sale_adv_pay_inv(
            self.env,
            sale_order,
            {"advance_payment_method": "percentage", "amount": 100},
        )
        down_payments.action_post()

        picking = sale_order.picking_ids
        picking.action_confirm()
        picking.action_assign()
        # Deliver 4 out of 10 -> backorder for the remaining 6
        picking.move_ids.quantity = 4.0
        create_with_form_pck_backorder(self.env, picking)
        self.assertEqual(picking.state, "done")

        with Form(
            self.env["stock.invoice.onshipping"].with_context(
                active_ids=picking.ids,
                active_model=picking._name,
            )
        ) as wizard_form:
            wizard_form.group = "partner_product"
            wizard_form.deduct_down_payments = deduct_down_payments
            wizard = wizard_form.save()
        self.assertEqual(wizard.deduct_down_payments, deduct_down_payments)

        invoices_before = sale_order.invoice_ids
        wizard.action_generate()
        invoices = sale_order.invoice_ids - invoices_before
        self.assertTrue(invoices, "Invoice was not created from the Picking.")
        # The Down Payments lines are on the Invoice, with or without the
        # option (only the refund switch depends on it)
        self.assertTrue(
            invoices.invoice_line_ids.filtered(
                lambda line: line.sale_line_ids.is_downpayment
            ),
            "Invoice without the Down Payment lines.",
        )
        return invoices
