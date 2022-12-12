# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Accounting partner category",
    "summary": """
        Add tags on partner to helps accountant
        to select journal entries easley based
        on dedicated partner category
        """,
    "version": "14.0.1.0.0",
    "author": "Pierre Verkest, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/account_partner_category.xml",
        "views/partner_view.xml",
    ],
    "maintainers": ["petrus-v"],
}
