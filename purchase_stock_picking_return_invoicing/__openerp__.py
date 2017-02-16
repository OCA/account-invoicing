# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Refund Returned Pickings in Purchase Orders",
    "summary": "Add an option to refund returned pickings",
    "version": "9.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_view.xml",
        "wizards/stock_return_picking_view.xml"
    ],
}
