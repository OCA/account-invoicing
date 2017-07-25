# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Picking Return Invoicing Open Qty",
    "summary": "This a glue module to combine two modules",
    "version": "9.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock_picking_return_invoicing",
        "purchase_open_qty",
    ],
    "data": [
        "views/purchase_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
