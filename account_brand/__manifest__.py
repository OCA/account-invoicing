# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Brand",
    "summary": "Send branded invoices and refunds",
    "version": "12.0.2.0.0",
    "category": "Accounting Management",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        'account',
        'partner_brand',
    ],
    "data": [
        "views/account_invoice.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["osi-scampbell"],
}
