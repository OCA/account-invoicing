# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Batch Invoicing",
    "summary": "Make invoices for all ready purchase orders",
    "version": "9.0.1.0.0",
    "category": "Purchases",
    "website": "https://tecnativa.com/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/purchase_batch_invoicing_view.xml",
    ],
    "images": [
        "static/description/wizard.png",
    ],
}
