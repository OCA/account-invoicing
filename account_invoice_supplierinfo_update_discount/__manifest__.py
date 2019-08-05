# coding: utf-8
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice - Supplier Info Update (Discount)',
    'summary': 'In the supplier invoice, automatically update all products '
               'whose discount on the line is different from '
               'the supplier discount',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'http://odoo-community.org',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'maintainers': ['legalsylvain'],
    'development_status': 'Beta',
    'depends': [
        'account_invoice_supplierinfo_update',
        'product_supplierinfo_discount',
    ],
    'installable': True,
    'auto_install': True,
    'data': [
        'wizard/wizard_update_invoice_supplierinfo.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/account_invoice.xml',
    ],
}
