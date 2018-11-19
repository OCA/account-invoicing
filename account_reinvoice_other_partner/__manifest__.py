# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Account Reinvoice Other Partner',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'http://github.com/OCA/account-invoicing',
    'category': 'Sale',
    'depends': [
        'account_invoicing',
    ],
    'license': 'LGPL-3',
    'data': [
        'wizard/account_reinvoice_other_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
