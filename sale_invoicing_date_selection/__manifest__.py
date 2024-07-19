# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Invoicing Date Selection",
    "summary": "Set date invoice when you create invoices",
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": ["wizard/sale_make_invoice_advance_views.xml"],
    "maintainers": ["sergio-teruel"],
}
