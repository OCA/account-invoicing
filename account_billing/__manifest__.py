# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Billing Process",
    "summary": "Group invoice as billing before payment",
    "version": "13.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account",
    "depends": ["account"],
    "data": [
        "data/account_billing_sequence.xml",
        "data/account_move.xml",
        "security/ir.model.access.csv",
        "views/account_billing_views.xml",
        "views/account_move_views.xml",
        "report/report_billing.xml",
        "report/report.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["Saran440"],
}
