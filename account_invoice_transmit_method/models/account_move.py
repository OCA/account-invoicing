# Copyright 2017-2020 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    transmit_method_id = fields.Many2one(
        "transmit.method",
        string="Transmission Method",
        compute="_compute_transmit_method_id",
        store=True,
        readonly=False,
        tracking=True,
        ondelete="restrict",
        domain="""
            [
                '|',
                ('customer_ok', '=', invoice_filter_type_domain in (False, 'sale')),
                ('supplier_ok', '=', invoice_filter_type_domain in (False, 'purchase')),
            ]
        """,
    )
    transmit_method_code = fields.Char(
        string="Transmission Method Code",
        related="transmit_method_id.code",
        help="Technical field used for UX purposes",
    )

    @api.depends("partner_id", "move_type")
    def _compute_transmit_method_id(self):
        for rec in self:
            if rec.partner_id and rec.is_sale_document():
                rec.transmit_method_id = (
                    rec.partner_id.customer_invoice_transmit_method_id
                )
            elif rec.partner_id and rec.is_purchase_document():
                rec.transmit_method_id = (
                    rec.partner_id.supplier_invoice_transmit_method_id
                )
            else:
                rec.transmit_method_id = False
