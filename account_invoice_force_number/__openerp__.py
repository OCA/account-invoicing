# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-2016 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Force Invoice Number",
    'version': '9.0.0.1.0',
    'category': 'Accounting & Finance',
    'summary': "Allows to force invoice numbering on specific invoices",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['base', 'account', 'product'],
    'data': [
        'security/security.xml',
        'views/invoice_view.xml'
    ],
    'test': ['test/invoice_force_number.yml'],
    "active": False,
    'installable': True,
}
