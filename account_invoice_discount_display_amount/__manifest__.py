# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Discount Display Amount",
    "summary": """
        Show total discount applied and total without
        discount on invoices.""",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "author": "Sygel,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["base", "account"],
    "data": [
        "views/account_move_views.xml",
        "report/report_invoice.xml",
    ],
}
