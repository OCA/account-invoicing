# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_account_tax_groups_with_notes(self):
        self.ensure_one()
        tax_groups = self.mapped("tax_line_ids.tax_id.tax_group_id")
        tax_groups = tax_groups.filtered(lambda g: g.report_note)
        return tax_groups
