# -*- coding: utf-8 -*-
# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase invoice no zero line",
    "summary": "Avoid the creation of zero quantity invoice lines from purchase",
    "version": "11.0.1.0.0",
    "category": "Purchase Management",
    "author": "Digital5 S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase",
    ],
    'data': [
        'views/account_view.xml',
    ],
}
