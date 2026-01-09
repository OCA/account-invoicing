# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    crm_tag_ids = fields.Many2many(
        comodel_name="crm.tag",
        relation="account_move_line_crm_tag_rel",
        column1="account_move_line_id",
        column2="crm_tag_id",
        string="Invoice CRM Tags",
        readonly=True,
    )
