# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

{
    "name": "Account Invoice Default Company Bank Sale",
    "summary": "Account Invoice Default Company Bank Sale",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "description": """This module allows to set Bank Account
                     from Invoices as Default Company Bank
                     from Partner when the invoice will
                     be created starting from Sale order or
                     from Stock picking.""",
    'website': 'http://www.serpentcs.com',
    "author": """Serpent Consulting Services Pvt. Ltd.,
                Agile Business Group,
                Odoo Community Association (OCA)""",
    "license": "LGPL-3",
    "depends": [
        "sale_stock",
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    "installable": True,
}
