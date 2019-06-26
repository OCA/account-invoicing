# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Ebill Payment Contract',
    'summary': """
        Base for ebilling addons""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': [
        'account_invoice_transmit_method',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ebill_payment_contract.xml',
    ],
    'demo': [
        'demo/ebill_payment_contract.xml',
    ],
}
