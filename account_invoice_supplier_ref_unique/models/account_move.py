# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    supplier_invoice_number = fields.Char(
        string="Vendor invoice number",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    @api.constrains("supplier_invoice_number")
    def _check_unique_supplier_invoice_number_insensitive(self):
        """
        Check if an other vendor bill has the same supplier_invoice_number
        and the same commercial_partner_id than the current instance
        """
        for rec in self:
            if rec.supplier_invoice_number and rec.is_purchase_document(
                include_receipts=True
            ):
                same_supplier_inv_num = rec.search(
                    [
                        ("commercial_partner_id", "=", rec.commercial_partner_id.id),
                        ("move_type", "in", ("in_invoice", "in_refund")),
                        (
                            "supplier_invoice_number",
                            "=ilike",
                            rec.supplier_invoice_number,
                        ),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if same_supplier_inv_num:
                    raise ValidationError(
                        _(
                            "The invoice/refund with supplier invoice number '%s' "
                            "already exists in Odoo under the number '%s' "
                            "for supplier '%s'."
                        )
                        % (
                            same_supplier_inv_num.supplier_invoice_number,
                            same_supplier_inv_num.name or "-",
                            same_supplier_inv_num.partner_id.display_name,
                        )
                    )

    @api.onchange("supplier_invoice_number")
    def _onchange_supplier_invoice_number(self):
        if not self.ref:
            self.ref = self.supplier_invoice_number

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # OVERRIDE
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            if (
                move
                and move.is_purchase_document(include_receipts=True)
                and default_values.get("ref")
            ):
                default_values.update({"ref": ""})
        return super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )

    def copy(self, default=None):
        """
        The unique vendor invoice number is not copied in vendor bills
        """
        if self.is_purchase_document(include_receipts=True):
            default = dict(default or {}, ref="")
        return super().copy(default)
