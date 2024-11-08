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
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.invoicing_mode = cls._invoicing_mode
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.partner2.invoicing_mode = cls._invoicing_mode
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.pt1 = cls.env["account.payment.term"].create({"name": "Term Two"})
        cls.pt2 = cls.env["account.payment.term"].create({"name": "Term One"})

        # Create a default pricelist for the test
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.env.ref("base.main_company").currency_id.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.so1 = cls.env["sale.order"].create(
            {
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
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        }
                    )
                ],
                "pricelist_id": cls.pricelist.id,  # Use the newly created pricelist
            }
        )
        # Lets give the saleorder the same partner and payment terms
        cls.so2 = cls.env["sale.order"].create(
            {
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
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.pricelist.id,  # Use the newly created pricelist
            }
        )
        cls.company = cls.so1.company_id

    @classmethod
    def _confirm_and_deliver(cls, sale_order):
        """
        Use standard sale flow to confirm delivered products
        """
        sale_order.action_confirm()
        for line in sale_order.order_line:
            line.qty_delivered = line.product_uom_qty
