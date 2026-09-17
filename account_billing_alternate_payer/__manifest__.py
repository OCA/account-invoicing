# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Billing Alternate Payer",
    "summary": "Group invoices in a billing document by their alternate payer",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "KMEE, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "account_billing",
        "account_invoice_alternate_payer",
    ],
    "data": [
        "views/account_billing_views.xml",
    ],
}
