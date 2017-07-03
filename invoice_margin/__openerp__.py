# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Invoice Margin',
    'version': '8.0.1.0.0',
    'category': 'Invoicing',
    'sequence': 1,
    'author': "GRAP,"
              "Odoo Community Association (OCA)",
    'summary': 'Margin on Account Invoices',
    'depends': [
        'account',
    ],
    'data': [
        'views/view_account_invoice.xml',
    ],
    'installable': True,
}
