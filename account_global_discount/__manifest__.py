# Copyright 2019 Tecnativa S.L. - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Global Discount",
    "version": "13.0.1.0.1",
    "category": "Accounting",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-backend",
    "license": "AGPL-3",
    "depends": ["account", "base_global_discount"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_invoice_views.xml",
        "views/global_discount_views.xml",
        "views/report_account_invoice.xml",
    ],
    "application": False,
    "installable": True,
}
