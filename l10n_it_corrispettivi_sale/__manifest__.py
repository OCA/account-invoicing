# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Italian Localization - Corrispettivi e ordini di vendita',
    'version': '10.0.1.0.1',
    'category': 'Accounting & Finance',
    'summary': 'Modulo per integrare i corrispettivi in odoo '
               'con gli ordini di vendita.',
    'author': 'Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-italy/tree/10.0/'
               'l10n_it_corrispettivi_sale',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_corrispettivi',
        'sale'
    ],
    'data': [
        'views/sale_view.xml'
    ],
    'installable': True,
    'auto-install': True,
}
