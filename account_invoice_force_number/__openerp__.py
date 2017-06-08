# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-2016 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Force Invoice Number",
    'version': '9.0.0.1.0',
    'category': 'Accounting & Finance',
    'summary': "Allows to force invoice numbering on specific invoices",
    'description': """
This module allows to force the invoice numbering.
It displays the internal_number field. If user fills that field, the typed
value will be used as invoice (and move) number.
Otherwise, the next sequence number will be retrieved and saved.
So, the new field has to be used when user doesn't want to use the default
invoice numbering for a specific invoice.""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['base', 'account', 'product'],
    'data': ['views/invoice_view.xml'],
    'test': ['test/invoice_force_number.yml'],
    "active": False,
    'installable': True,
}
