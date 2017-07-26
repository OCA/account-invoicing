# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Invoice Analytic Search',
    'summary': 'Search invoices by analytic account or by project manager',
    'version': '10.0.1.0.0',
    'author': 'Project Expert Team,'
              'Eficent,'
              'Odoo Community Association (OCA)',
    'contributors': [
        'Jordi Ballester <jordi.ballester@eficent.com>',
        'Matjaž Mozetič <m.mozetic@matmoz.si>',
    ],
    'website': 'http://project.expert',
    'license': 'AGPL-3',
    'category': 'Project Management',
    'depends': [
        'analytic',
        'account'
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
