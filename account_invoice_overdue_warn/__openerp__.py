# -*- coding: utf-8 -*-
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Warning on Overdue Invoices",
    "version": "8.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Show warning on customer form view if it has overdue invoices",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/credit-control",
    "depends": ["account"],
    "data": [
        "views/res_partner.xml",
    ],
    "installable": True,
}
