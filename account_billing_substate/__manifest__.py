# Copyright 2024 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Billing - Sub State",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account_billing", "base_substate"],
    "data": [
        "data/account_billing_substate_mail_template_data.xml",
        "data/account_billing_substate_data.xml",
        "views/account_billing_views.xml",
    ],
    "demo": ["demo/account_billing_substate_demo.xml"],
    "installable": True,
}
