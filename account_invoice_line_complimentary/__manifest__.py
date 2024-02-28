#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "Complimentary Invoice Line",
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': "Define Invoice Lines for complimentary Products.",
    'author': "TAKOBI, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing'
               '/tree/12.0/account_invoice_line_complimentary',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_line_views.xml',
        'views/account_invoice_views.xml',
        'views/res_config_settings_views.xml',
    ],
}
