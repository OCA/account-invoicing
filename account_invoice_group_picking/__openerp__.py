# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Group Picking",
    "summary": "Print invoice lines grouped by picking",
    "version": "9.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/report_invoice.xml",
    ],
}
