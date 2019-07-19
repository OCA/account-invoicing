# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Account Invoice Payments Report",
    "summary": "Display existing payment on invoice report",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_report.xml",
        "views/report_invoice.xml",
    ],
}
