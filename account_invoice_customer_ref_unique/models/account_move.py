# Copyright 2016 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_invoice_number = fields.Char(
        string="Customer invoice number",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    @api.constrains("customer_invoice_number")
    def _check_unique_customer_invoice_number_insensitive(self):
        """
        Check if an other customer invoice has the same customer_invoice_number
        and the same commercial_partner_id than the current instance
        """
        for rec in self:
            if rec.customer_invoice_number and rec.is_sale_document(
                include_receipts=True
            ):
                same_customer_inv_num = rec.search(
                    [
                        ("commercial_partner_id", "=", rec.commercial_partner_id.id),
                        ("move_type", "in", ("out_invoice", "out_refund")),
                        (
                            "customer_invoice_number",
                            "=ilike",
                            rec.customer_invoice_number,
                        ),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if same_customer_inv_num:
                    raise ValidationError(
                        _(
                            "The invoice/refund with customer invoice number {} "
                            "already exists in Odoo under the number {} "
                            "for customer {}."
                        ).format(
                            same_customer_inv_num.customer_invoice_number,
                            same_customer_inv_num.name or "-",
                            same_customer_inv_num.partner_id.display_name,
                        )
                    )

    @api.onchange("customer_invoice_number")
    def _onchange_customer_invoice_number(self):
        if not self.ref:
            self.ref = self.customer_invoice_number

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # OVERRIDE
        if default_values_list:
            for move, default_values in zip(self, default_values_list):
                if (
                    move
                    and move.is_sale_document(include_receipts=True)
                    and default_values.get("ref")
                ):
                    default_values.update({"ref": ""})
        return super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )

    def copy(self, default=None):
        """
        The unique customer invoice number is not copied in customer invoices
        """
        if self.is_sale_document(include_receipts=True):
            default = dict(default or {}, ref="")
        return super().copy(default)
