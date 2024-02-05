# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice - Discount Supplier Info Update',
    'summary': 'In the supplier invoice, automatically update all products '
               'whose discount on the line is different from '
               'the supplier discount',
    'version': '12.0.1.1.0',
    'category': 'Accounting & Finance',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'maintainers': ['legalsylvain'],
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_supplierinfo_update',
        'purchase_discount',
    ],
    'installable': True,
    'auto_install': True,
    'data': [
        'wizard/wizard_update_invoice_supplierinfo.xml',
    ],
}
