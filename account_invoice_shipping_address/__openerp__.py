# -*- coding: utf-8 -*-
# Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
# Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# Copyright 2017 Apulia Software srl - www.apuliasoftware.it
# Author Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Shipping Address",
    'summary': """
        Adds a shipping address field to the invoice.""",
    "version": "8.0.0.1.1",
    'category': 'Generic Modules/Accounting',
    "depends": ["account", "sale", "sale_stock"],
    "author": "Apulia Software srl, Agile Business Group,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.odoo-community.org',
    'license': 'AGPL-3',
    'data': [
        'invoice_view.xml',
    ],
    'installable': True,
}
