# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Account invoice tax note",
    'version': "11.0.1.0.0",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "summary": "Print tax notes on customer invoices",
    'website': "https://github.com/OCA/account-invoicing",
    'category': "Localization / Accounting",
    'license': "AGPL-3",
    'depends': [
        "account",
    ],
    'data': [
        'reports/report_invoice_document.xml',
    ],
    'installable': True,
}
