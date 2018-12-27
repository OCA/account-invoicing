# -*- coding: utf-8 -*-
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

{
    "name": "Purchase Self Invoice",
    "version": "11.0.2.0.0",
    "author": "Creu Blanca, "
              "Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/account_invoice_views.xml",
        "views/report_self_invoice.xml"
    ],
    "installable": True,
}
