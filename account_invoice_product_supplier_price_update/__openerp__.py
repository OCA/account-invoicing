# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Product Supplier Price Update',
    'summary': 'In the supplier invoice, automatically update all products '
               'whose unit price on the line is different from '
               'the supplier price',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'http://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account',
        'product_supplierinfo_tree_price_info',
        'product_variant_supplierinfo'
    ],
    'data': [
        'account_invoice_view.xml',
        'wizard/update_supplier_price.xml'
    ],
    'demo': [
        'demo/product_supplierinfo.xml',
        'demo/account_invoice.xml',
    ],
}
