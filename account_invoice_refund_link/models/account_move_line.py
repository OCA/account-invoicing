# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2018 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    origin_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Original invoice line",
        help="Original invoice line to which this refund invoice line "
        "is referred to",
        copy=False,
        index=True,
    )
    refund_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="origin_line_id",
        string="Refund invoice lines",
        help="Refund invoice lines created from this invoice line",
        copy=False,
    )
