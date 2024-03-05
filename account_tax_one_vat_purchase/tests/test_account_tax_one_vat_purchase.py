# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account_tax_one_vat.tests.common import TestAccountTaxOneVatCommon


@tagged("post_install", "-at_install")
class TestAccountTaxOneVatPurchase(TestAccountTaxOneVatCommon):
    def test_po_line_without_limitation(self):
        """
        No constraint
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        po_line.taxes_id = [Command.set(self.vat_taxes.ids)]
        self.assertEqual(po_line.taxes_id, self.vat_taxes)

    def test_po_line_with_limitation_constraint(self):
        """
        - The constraint triggers an error trying to set 2 VAT taxes on po line
        """
        # set the one vat tax only
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        msg = "Multiple customer tax of type VAT are selected. Only one is allowed."
        with self.assertRaises(ValidationError, msg=msg):
            po_line.taxes_id = [Command.set(self.vat_taxes.ids)]
        nb_vat_taxes = len(po_line.taxes_id.filtered("is_vat"))
        self.assertEqual(nb_vat_taxes, 0)

    def test_po_lines_with_limitation_no_constraint(self):
        """
        - The constraint doesn't trigger the error if we set 2 taxes containing
          only one VAT
        """
        # set the one vat tax only
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        po_line = po.order_line[0]
        po_line.taxes_id = [Command.set(self.mixed_taxes.ids)]
        self.assertEqual(len(po_line.taxes_id), 2)
        nb_vat_taxes = len(po_line.taxes_id.filtered("is_vat"))
        self.assertEqual(nb_vat_taxes, 1)
