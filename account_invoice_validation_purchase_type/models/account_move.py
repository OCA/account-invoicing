# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    product_type_id = fields.Many2one(
        comodel_name="product.product",
        string="Purchase type",
        help="Technical field used for the Invoice validation widget",
        domain=[("purchase_type", "=", True), ("active", "=", True)],
    )

    def update_move_line_with_product_type(self):
        moves = self.filtered(lambda m: m.move_type in m.get_concerned_types())
        lines = moves.invoice_line_ids.filtered(lambda l: l.display_type == "product")
        for line in lines:
            data = line.move_id.update_move_line_data(line)
            line.write(data)
            line._compute_totals()

    def update_move_line_data(self, line):
        product = self.product_type_id
        taxes = product.supplier_taxes_id
        expense_account = product.property_account_expense_id
        name = line.name
        price_unit = line.price_unit
        return {
            "product_id": product.id,
            "name": name,
            "price_unit": price_unit,
            "tax_ids": [Command.set(taxes.ids)],
            "account_id": expense_account.id,
        }

    def write(self, vals):
        res = super().write(vals)
        if "product_type_id" in vals:
            self.update_move_line_with_product_type()
        return res
