# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account invoice merge with picking links",
    "summary": "Merge invoices linked to pickings",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "http://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "account_invoice_merge",
        "stock_picking_invoice_link",
    ],
}
