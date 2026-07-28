# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Account Move Pivot View",
    "summary": """
        Adds pivot view to Invoices (move in and move out), Refunds, and Receipts
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": ["views/account_move_views.xml"],
    "uninstall_hook": "uninstall_hook",
}
