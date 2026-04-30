# Copyright 2020 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class CommonPartnerInvoicingMode(BaseCommon):
    _invoicing_mode = "standard"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountPaymentTerm = cls.env["account.payment.term"]
        cls.Partner = cls.env["res.partner"]
        cls.ProductPriceList = cls.env["product.pricelist"]
        cls.company = cls.env.company
        cls.partner = cls._create_partner("Partner Invoicing Mode 1")
        cls.partner2 = cls._create_partner("Partner Invoicing Mode 2")
        (cls.partner | cls.partner2).invoicing_mode = cls._invoicing_mode
        cls.product = cls._create_product()
        cls.pt1, cls.pt2 = cls._create_payment_terms(2)

        cls.pricelist = cls.ProductPriceList.create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.company.currency_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.so1, cls.so2 = cls._create_sale_orders(2)
        cls.invoice1, cls.invoice2 = cls._create_invoices(2)
        cls.cron = cls.env.ref(
            "partner_invoicing_mode.ir_cron_generate_standard_invoice"
        )

    @classmethod
    def _create_partner(cls, name, **vals):
        partner_vals = {"name": name}
        partner_vals.update(vals)
        return cls.Partner.create(partner_vals)

    @classmethod
    def _create_product(cls, **vals):
        product_vals = {
            "name": "Partner Invoicing Mode Product",
            "type": "service",
            "invoice_policy": "delivery",
            "list_price": 123,
            "taxes_id": [Command.clear()],
            "supplier_taxes_id": [Command.clear()],
            "company_id": cls.company.id,
        }
        product_vals.update(vals)
        return cls.env["product.product"].create(product_vals)

    @classmethod
    def _create_payment_terms(cls, count, **vals):
        payment_terms_vals = [
            {"name": f"Test Payment Term {index}", **vals}
            for index in range(1, count + 1)
        ]
        return cls.AccountPaymentTerm.create(payment_terms_vals)

    @classmethod
    def _prepare_sale_order_vals(cls, **vals):
        sale_order_vals = {
            "partner_id": cls.partner.id,
            "partner_invoice_id": cls.partner.id,
            "partner_shipping_id": cls.partner.id,
            "payment_term_id": cls.pt1.id,
            "order_line": [
                Command.create(
                    {
                        "name": "Line one",
                        "product_id": cls.product.id,
                        "product_uom_qty": 4,
                        "product_uom_id": cls.product.uom_id.id,
                        "price_unit": 123,
                    }
                )
            ],
            "pricelist_id": cls.pricelist.id,
        }
        sale_order_vals.update(vals)
        return sale_order_vals

    @classmethod
    def _create_sale_orders(cls, count, **vals):
        return cls.SaleOrder.create(
            [cls._prepare_sale_order_vals(**vals) for _i in range(count)]
        )

    @classmethod
    def _prepare_invoice_vals(cls, **vals):
        invoice_vals = {
            "move_type": "out_invoice",
            "partner_id": cls.partner.id,
            "invoice_date": "2026-04-01",
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": "Line one",
                        "product_id": cls.product.id,
                        "quantity": 1,
                        "price_unit": 50.0,
                        "tax_ids": [Command.clear()],
                    }
                )
            ],
        }
        invoice_vals.update(vals)
        return invoice_vals

    @classmethod
    def _create_invoices(cls, count, **vals):
        return cls.AccountMove.create(
            [cls._prepare_invoice_vals(**vals) for _i in range(count)]
        )

    @classmethod
    def _confirm_and_deliver(cls, sale_order):
        """
        Use standard sale flow to confirm delivered products
        """
        sale_order.action_confirm()
        for line in sale_order.order_line:
            line.qty_delivered = line.product_uom_qty
