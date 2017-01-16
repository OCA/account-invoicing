# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Account Partner Journal',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Define default journal on partner',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'purchase',
    ],
    'data': [
        "views/res_partner_view.xml",
    ],
    'installable': True,
}
