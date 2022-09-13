# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account Move Post Block",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "15.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account_move_exception"],
    "data": [
        "data/account_exception_data.xml",
        "security/ir.model.access.csv",
        "security/account_move_post_block_security.xml",
        "views/account_post_block_reason_view.xml",
        "views/account_move_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
