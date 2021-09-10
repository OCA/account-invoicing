# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Sub State",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account", "base_substate"],
    "data": [
        "data/account_move_substate_mail_template_data.xml",
        "data/account_move_substate_data.xml",
        "views/account_move_views.xml",
    ],
    "demo": ["demo/account_move_substate_demo.xml"],
    "installable": True,
}
