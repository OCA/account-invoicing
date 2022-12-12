# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale accounting partner category",
    "summary": """This is a glue module between `sale` and `accounting_partner_category`""",
    "version": "14.0.1.0.0",
    "author": "Pierre Verkest, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "accounting_partner_category",
        "sale",
    ],
    "data": [],
    "maintainers": ["petrus-v"],
    "installable": True,
    "auto-install": True,
}
