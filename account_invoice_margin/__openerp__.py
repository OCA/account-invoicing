# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Invoice Margin",
    "summary": "Show margin in invoices",
    "version": "9.0.1.0.0",
    "category": "Account",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        'security/account_invoice_margin_security.xml',
        'views/account_invoice_margin_view.xml',
    ],
}
