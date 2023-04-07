# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimounee@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_budget = fields.Boolean(
        "Is a customer budget",
        help="Check this box if the journal is used for manage customer budget.\n"
        "The journal must have a sale type",
    )
