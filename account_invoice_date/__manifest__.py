# © 2022 Thomas Rehn (initOS GmbH)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Date",
    "summary": """
    When an invoice or bill is validated from Draft to Open automatically,
    the invoice/bill date is set to current date.
    If an invoice/bill is validated from Draft to Open manually,
    a window is displayed to query the invoice/bill date from the user.
    """,
    "category": "Accounting",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_voucher_proforma_date_view.xml",
        "views/account_move_view.xml",
    ],
    "author": "initOS,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
}
