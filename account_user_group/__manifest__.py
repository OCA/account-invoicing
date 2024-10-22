# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account User Group",
    "summary": "Limits accounting user functionality depending on the groups",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainers": ["smaciasosi", "max3903"],
    "license": "AGPL-3",
    "depends": ["account", "account_edi"],
    "data": [
        "security/account_user_group_security.xml",
        "security/ir.model.access.csv",
        "views/account_user_group_views.xml",
    ],
}
