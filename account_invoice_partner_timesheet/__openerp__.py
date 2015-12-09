# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Account invoice partner timesheet",

    'summary': """
        Provide a compatibility between account_invoice_partner and
        hr_timesheet_invoice""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Accounting & Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_partner',
        'hr_timesheet_invoice'
    ],
    'data': [],
    'auto_install': True,
}
