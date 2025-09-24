# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fixed Triple Discount",
    "summary": "Compatibility between fixed and triple discount modules",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_invoice_fixed_discount", "account_invoice_triple_discount"],
    "auto_install": True,
    "data": ["views/account_move_view.xml"],
}
