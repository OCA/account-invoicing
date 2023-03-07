{
    'name': 'Account invoice merge auto',
    'category': 'Accounting',
    'summary': "",
    'version': '12.0.0.0.1',
    'author': "Odoo Community Association (OCA)",
    'license': "AGPL-3",
    'website': "https://github.com/OCA/account-invoicing",
    'depends': [
        'account_invoice_merge',
    ],
    'external_dependencies': {
    },
    'data': [
        'data/crontab.xml',
        'views/res_partner.xml',
        'views/account_invoice.xml',
    ],
    'installable': True,
}
