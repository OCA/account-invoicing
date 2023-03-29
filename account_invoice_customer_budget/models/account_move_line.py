# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimounee@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    budget_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Budget",
        readonly=False,
        index=True,
        domain="['|', '|', ('partner_id', '=', partner_id), ('partner_id', 'child_of', partner_id), ('partner_id', 'parent_of', partner_id), ('is_budget', '=', True)]",
    )

    @api.constrains('partner_id', 'budget_invoice_id')
    def _check_budget_invoice_partner(self):
        for line in self:
            budget_partner = line.budget_invoice_id.partner_id.commercial_partner_id
            if budget_partner and line.partner_id != budget_partner:
                    raise UserError(_("You can not consume a budget of an other customer. Please select the right budget"))
