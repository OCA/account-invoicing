# -*- coding: utf-8 -*-
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Warning on Overdue Invoices - Sale",
    "version": "8.0.1.0.0",
    "category": "Sales/Sales",
    "license": "AGPL-3",
    "summary": "Show overdue warning on sale order form view",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/credit-control",
    "depends": ["sale", "account_invoice_overdue_warn"],
    "data": [
        "views/sale_order.xml",
    ],
    "installable": True,
}
