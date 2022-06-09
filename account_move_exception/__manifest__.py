# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Move Exception",
    "summary": "Custom exceptions on account move",
    "version": "15.0.1.0.0",
    "category": "Generic Modules/Account",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "data/account_exception_data.xml",
        "security/ir.model.access.csv",
        "wizard/account_exception_confirm_view.xml",
        "views/account_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
