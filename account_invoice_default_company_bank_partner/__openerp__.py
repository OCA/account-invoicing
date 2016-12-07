# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

{
    "name": "Account Invoice Default Company Bank Partner",
    "summary": "Account Invoice Default Company Bank Partner",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    'website': 'http://www.serpentcs.com',
    "author": """Serpent Consulting Services Pvt. Ltd.,
                Agile Business Group,
                Odoo Community Association (OCA)""",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    "installable": True,
}
