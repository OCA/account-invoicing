# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018-2019 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Italian Localization - Ricevute e ordini di vendita',
    'version': '12.0.1.0.3',
    'category': 'Accounting & Finance',
    'summary': 'Modulo per integrare le ricevute in Odoo '
               'con gli ordini di vendita.',
    'author': 'Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-italy'
               '/tree/12.0/l10n_it_corrispettivi_sale',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_corrispettivi',
        'sale_management'
    ],
    'data': [
        'views/sale_view.xml'
    ],
    'installable': True,
    'auto_install': True,
}
