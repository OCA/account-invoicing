# Copyright 2015 - Camptocamp SA - Author Vincent Renaville
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Tax required in invoice",
    'version': "12.0.1.0.0",
    "author": "Camptocamp,Tecnativa,Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/account-invoicing",
    'category': "Localization / Accounting",
    'license': "AGPL-3",
    'summary': '''This module adds functional a check on invoice to force user
        to set tax on invoice line.''',
    'depends': [
        "account",
    ],
    'installable': True,
}
