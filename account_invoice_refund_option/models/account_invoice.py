# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_refund = fields.Boolean(
        string="Is a refund?",
        compute="_compute_is_refund",
        inverse="_inverse_is_refund",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Indicate if this invoice is a refund.",
    )

    @api.multi
    @api.depends("type")
    def _compute_is_refund(self):
        """Know if this invoice is a refund or not."""
        for one in self:
            one.is_refund = one.type.endswith("_refund")

    @api.multi
    def _inverse_is_refund(self):
        for one in self:
            args = "refund", "invoice"
            if one.is_refund:
                args = reversed(args)
            one.type = one.type.replace(*args)
