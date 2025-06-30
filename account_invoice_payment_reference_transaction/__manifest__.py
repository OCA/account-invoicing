# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account invoice Payment Reference Payment Transaction",
    "summary": """
        Use the payment transaction as payment reference for reconciliation
        """,
    "author": "BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Invoicing",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "account_payment",
        "sale",  # for flow testing
    ],
}
