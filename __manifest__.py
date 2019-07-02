{
    'name': 'Account invoice merge auto',
    'category': 'Accounting',
    'summary': "",
    'version': '10.0.0.0.1',
    'author': "Commown SCIC SAS",
    'license': "AGPL-3",
    'website': "https://commown.fr",
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
