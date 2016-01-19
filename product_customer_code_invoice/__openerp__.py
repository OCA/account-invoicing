# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Product Customer code for Account Invoice",
    "version": "8.0.1.0.0",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "website": "http://www.agilebg.com",
    "license": 'AGPL-3',
    "category": 'Accounting & Finance',
    "depends": [
        'product_customer_code',
        'account',
    ],
    "data": ['views/account_invoice_view.xml'],
    "installable": True,
}
