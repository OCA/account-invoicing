# Copyright 2018 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_account_tax_groups_with_notes(self):
        self.ensure_one()
        for line in self:
            tax_groups = line.mapped("invoice_line_ids.tax_ids.tax_group_id")
            tax_groups = tax_groups.filtered(lambda g: g.report_note)
        return tax_groups
