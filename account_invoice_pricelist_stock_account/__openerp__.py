# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Pricelist - Stock Account',
    'summary': 'Set pricelist from SO / PO in invoice created from picking',
    'author': 'Therp BV,GRAP,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://github.com/OCA/account-invoicing',
    'category': 'Invoicing',
    'version': '8.0.1.0.0',
    'depends': [
        'account_invoice_pricelist',
        'stock_account',
    ],
    'installable': True,
    'auto_install': True,
}
