# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Refund Return Pickings in Sales Orders",
    "summary": "Add an option to refund return pickings",
    "version": "9.0.1.0.0",
    "category": "Sales",
    "website": "https://tecnativa.com/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "wizards/stock_return_picking_view.xml",
    ],
}
