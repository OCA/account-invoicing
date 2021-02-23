# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Portal Hide Invoices & Bills",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Hide Invoices & Bills from customer portal if not available.",
    "author": "Pordenone Linux User Group (PNLUG), Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["views/account_portal_templates.xml"],
    "installable": True,
}
