# -*- coding: utf-8 -*-
# © 2011 Domsense s.r.l. (<http://www.domsense.com>).
# © 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# © 2016 Farid Shahy (<fshahy@gmail.com>)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Invoice Shipping Address",
    "summary": "Add shipping address to customer invoices.",
    "version": "10.0.0.1.1",
    "category": "Generic Modules/Accounting",
    "author": "Andrea Cometa, Agile Business Group,"
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "images": [],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "sale",
        "sale_stock"
    ],
    "data": [
        "views/account_invoice.xml",
        "views/report_invoice.xml",
    ],
}
