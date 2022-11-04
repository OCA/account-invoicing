# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    property_refund_payment_term_id = fields.Many2one(
        "account.payment.term",
        company_dependent=True,
        string="Customer refund Payment Terms",
        domain="[('company_id', 'in', [current_company_id, False])]",
        help="This payment term will be used instead of the default one for customer refunds",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["property_refund_payment_term_id"]
