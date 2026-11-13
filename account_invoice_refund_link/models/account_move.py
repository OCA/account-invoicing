# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2022 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    refund_invoice_ids = fields.One2many(
        related="reversal_move_ids", string="Refund Invoices", readonly=True
    )

    def copy_data(self, default=None):
        """Don't link the copied lines when the copy is not a reversal, like the
        new draft invoice created by the "Reverse and Create Invoice" option of
        the reversal wizard. Only the reversal copy gets ``reversed_entry_id`` in
        the default values, so we use it to tell them apart.
        """
        if self.env.context.get("link_origin_line") and not (default or {}).get(
            "reversed_entry_id"
        ):
            return super(
                AccountMove, self.with_context(link_origin_line=False)
            ).copy_data(default=default)
        return super().copy_data(default=default)
