# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account_tax_one_vat.tests.common import TestAccountTaxOneVatCommon


@tagged("post_install", "-at_install")
class TestAccountTaxOneVatPurchase(TestAccountTaxOneVatCommon):
    def test_so_line_without_limitation(self):
        """
        No constraint
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [(0, 0, {"product_id": self.product_a.id})],
            }
        )
        so_line = so.order_line[0]
        so_line.tax_id = [Command.set(self.vat_taxes.ids)]
        self.assertEqual(so_line.tax_id, self.vat_taxes)

    def test_so_line_with_limitation_constraint(self):
        """
        - The constraint triggers an error trying to set 2 VAT taxes on po line
        """
        # set the one vat tax only
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [Command.create({"product_id": self.product_a.id})],
            }
        )
        so_line = so.order_line[0]
        msg = "Multiple customer tax of type VAT are selected. Only one is allowed."
        with self.assertRaises(ValidationError, msg=msg):
            so_line.tax_id = [Command.set(self.vat_taxes.ids)]
        nb_vat_taxes = len(so_line.tax_id.filtered("is_vat"))
        self.assertEqual(nb_vat_taxes, 0)

    def test_so_line_with_limitation_no_constraint(self):
        """
        - The constraint doesn't trigger the error if we set 2 taxes containing
          only one VAT
        """
        # set the one vat tax only
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [Command.create({"product_id": self.product_a.id})],
            }
        )
        so_line = so.order_line[0]
        so_line.tax_id = [(6, 0, self.mixed_taxes.ids)]
        self.assertEqual(len(so_line.tax_id), 2)
        nb_vat_taxes = len(so_line.tax_id.filtered("is_vat"))
        self.assertEqual(nb_vat_taxes, 1)
