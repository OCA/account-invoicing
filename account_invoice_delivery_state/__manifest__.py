# Copyright 2026 Allied Vision Technologies Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Delivery State",
    "version": "19.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Allied Vision Technologies Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "maintainers": ["pratikgunjal-maker"],
    "development_status": "Beta",
    "depends": [
        "account",
        "sale_stock",
        "purchase_stock",
    ],
    "data": [
        "views/account_move_views.xml",
        "views/account_portal_templates.xml",
    ],
    "installable": True,
}
