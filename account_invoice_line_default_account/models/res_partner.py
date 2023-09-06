# Copyright 2012 Therp BV (<http://therp.nl>)
# Copyright 2013-2018 BCIM SPRL (<http://www.bcim.be>)
# Copyright 2022 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_account_income = fields.Many2one(
        "account.account",
        string="Default Income Account",
        domain=lambda model: [
            (
                "user_type_id",
                "=",
                model.env.ref("account.data_account_type_revenue").id,
            ),
        ],
        help="Default counterpart account for sales on invoice lines",
        company_dependent=True,
    )
    auto_update_account_income = fields.Boolean(
        "Autosave Selection for Income Account on Invoice Line",
        help="When an account is selected on an invoice line, "
        "automatically assign it as default income account",
        default=True,
    )
    property_account_expense = fields.Many2one(
        "account.account",
        string="Default Expense Account",
        domain=lambda model: [
            (
                "user_type_id",
                "=",
                model.env.ref("account.data_account_type_expenses").id,
            ),
        ],
        help="Default counterpart account for purchases on invoice lines",
        company_dependent=True,
    )
    auto_update_account_expense = fields.Boolean(
        "Autosave Selection for Expense Account on Invoice Line",
        help="When an account is selected on an invoice line, "
        "automatically assign it as default expense account",
        default=True,
    )
