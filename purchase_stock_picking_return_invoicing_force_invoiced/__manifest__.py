# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Picking Return Invoicing Force Invoiced",
    "summary": "Glue module between purchase_force_invoiced "
               "and purchase_stock_picking_return_invoicing",
    "version": "11.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "development_status": "Beta",
    "depends": [
        "purchase_force_invoiced",
        "purchase_stock_picking_return_invoicing",
    ],
    "maintainers": [
        'jbeficent',
    ],
}
