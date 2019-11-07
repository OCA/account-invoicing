# Copyright 2016 Camptocamp SA
# Copyright 2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Unit rounded invoice',
 'version': '11.0.1.0.0',
 'category': 'Accounting',
 'author': "initOS GmbH, Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'website': 'https://github.com/initOS/account-invoicing',
 'license': 'AGPL-3',
 'depends': ['account_invoicing'],
 'data': [
         'views/res_config_settings_views.xml',
         'views/account_invoice_line_views.xml',
 ],
 'installable': True,
 'auto_install': False,
 'application': True,
 }
