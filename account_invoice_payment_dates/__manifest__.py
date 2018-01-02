# -*- coding: utf-8 -*-
# © 2017 Giacomo Grasso - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
{
    'name': 'Invoice Payment Deadlines',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Adding payment deadlines on sale invoice',
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'account'],
    'data': [
        'report/account_invoice.xml',
    ],
    'installable': True,
}
