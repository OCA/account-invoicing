# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import Form
from odoo.tests.common import SavepointCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestAccountInvoiceMergePurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMergePurchase, cls).setUpClass()
        cls.invoice_model = cls.env["account.move"].with_context(move_type="in_invoice")
        cls.purchase_model = cls.env["purchase.order"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product = cls.env.ref("product.product_product_8")
        cls.wiz = cls.env["invoice.merge"]

    def test_picking_multi_purchase_order(self):
        po_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_qty": 7.0,
                        "product_uom": self.product.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                )
            ],
        }
        po1 = self.purchase_model.create(po_vals)
        po2 = po1.copy()

        po1.button_confirm()
        po2.button_confirm()

        self.assertEqual(
            po1.picking_count, 1, 'Purchase: one picking should be created"'
        )
        self.assertEqual(
            po2.picking_count, 1, 'Purchase: one picking should be created"'
        )

        pi1 = po1.picking_ids[0]
        pi2 = po2.picking_ids[0]

        pi1.move_line_ids.write({"qty_done": 7.0})
        pi2.move_line_ids.write({"qty_done": 7.0})
        pi1.button_validate()
        pi2.button_validate()
        self.assertEqual(
            po1.order_line.mapped("qty_received"),
            [7.0],
            'Purchase: all products should be received"',
        )

        self.assertEqual(
            po2.order_line.mapped("qty_received"),
            [7.0],
            'Purchase: all products should be received"',
        )

        move_form1 = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form1.partner_id = self.partner
        move_form1.purchase_id = po1
        inv1 = move_form1.save()

        move_form2 = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form2.partner_id = self.partner
        move_form2.purchase_id = po2
        inv2 = move_form2.save()

        invoices = inv1 | inv2
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.invoice_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner.id)]
        )

        self.assertEqual(len(end_inv.invoice_line_ids.ids), 2)

        from_po = [po1.order_line.id, po2.order_line.id]
        from_inv = [
            end_inv.invoice_line_ids[0].purchase_line_id.id,
            end_inv.invoice_line_ids[1].purchase_line_id.id,
        ]
        self.assertListEqual(from_po, from_inv)

        end_inv.write(
            {"invoice_date": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}
        )

        end_inv.action_post()

        self.assertEqual(
            po1.invoice_status, "invoiced", 'Purchase: should be invoiced"'
        )

        self.assertEqual(
            po2.invoice_status, "invoiced", 'Purchase: should be invoiced"'
        )

        self.assertEqual(
            po1.order_line.mapped("qty_invoiced"),
            [7.0],
            'Purchase: all products should be invoiced"',
        )

        self.assertEqual(
            po2.order_line.mapped("qty_invoiced"),
            [7.0],
            'Purchase: all products should be invoiced"',
        )
