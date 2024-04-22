# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Account Fixed Discount",
    "summary": "Allows to apply fixed amount discounts in invoices.",
    "version": "16.0.1.0.4",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account"],
    "data": [
        "security/res_groups.xml",
        "views/account_move_view.xml",
        "reports/report_account_invoice.xml",
    ],
}
