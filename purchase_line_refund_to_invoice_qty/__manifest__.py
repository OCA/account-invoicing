# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Line Refund To Invoice Qty",
    "version": "18.0.1.0.0",
    "summary": """
        Allow deciding whether refunded quantity should be considered
        as quantity to reinvoice.
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["purchase"],
    "data": [
        "views/account_move_views.xml",
        "views/purchase_order_views.xml",
        "wizards/account_move_reversal_view.xml",
    ],
}
