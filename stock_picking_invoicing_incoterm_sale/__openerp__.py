# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock picking invoicing incoterm sale',
    'summary': 'Copy incoterm from sale to invoice and to picking',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'stock_picking_invoicing_incoterm',
        'sale',
    ],
    'installable': True,
}
