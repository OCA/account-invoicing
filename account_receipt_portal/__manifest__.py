# Copyright 2024 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Website Portal for Receipts",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Add sale and purchase receipts in the customer portal",
    "author": "Pordenone Linux User Group (PNLUG), Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account", "portal", "account_receipt_base", "account_receipt_print"],
    "data": [
        "views/account_portal_templates.xml",
        "security/account_security.xml",
    ],
    "installable": True,
}
