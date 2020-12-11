# © 2016 Chafique DELLI @ Akretion
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice - Supplier Info Update',
    'summary': 'In the supplier invoice, automatically updates all products '
               'whose unit price on the line is different from '
               'the supplier price',
    'version': '11.0.1.0.1',
    'category': 'Accounting & Finance',
    'website': 'https://github.com/OCA/account-invoicing',
    'author':
        'initOS GmbH,'
        'Akretion,'
        'GRAP,'
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'account_invoicing',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'wizard/wizard_update_invoice_supplierinfo.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
}
