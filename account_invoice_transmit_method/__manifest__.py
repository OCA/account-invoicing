# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Invoice Transmit Method',
    'version': '12.0.2.0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Configure invoice transmit method (email, post, portal, ...)',
    'author': 'Akretion, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'views/res_config_settings.xml',
        'wizards/account_invoice_send.xml',
        'security/ir.model.access.csv',
        'views/transmit_method.xml',
        'views/account_invoice.xml',
        'views/partner.xml',
        'data/transmit_method.xml',
    ],
    'demo': ['demo/partner.xml'],
    'installable': True,
}
