# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    crm_tag_ids = fields.Many2many(
        comodel_name="crm.tag",
        string="Invoice CRM tags",
        relation="account_move_crm_tag_rel",
        column1="account_move_id",
        column2="crm_tag_id",
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # As the invoice report is per line, we need to have a table that links invoice
    # lines with the header CRM tags, so although is somehow "noise", it's needed
    crm_tag_ids = fields.Many2many(
        comodel_name="crm.tag",
        string="Invoice CRM tags",
        related="move_id.crm_tag_ids",
        store=True,
        relation="account_move_line_crm_tag_rel",
        column1="account_move_line_id",
        column2="crm_tag_id",
    )
