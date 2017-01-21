# -*- coding: utf-8 -*-
# © 2016 <OCA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Invoice Fiscal Position Update',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Changing the fiscal position of an invoice will auto-update '
               'invoice lines',
    'description': """
Invoice Fiscal Position Update
==============================

With this module, when a user changes the fiscal position of an invoice, the
taxes and the accounts on all the invoice lines which have a product are
automatically updated. The invoice lines without a product are not updated and
a warning is displayed to the user in this case.
""",
    'author': "Julius Network Solutions,"
              "Akretion,"
              "Odoo Community Association (OCA)",
    'depends': ['account'],
    'data': [],
    'installable': True,
}
