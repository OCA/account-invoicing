# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Refund Reason',
    'version': '12.0.1.0.1',
    "summary": "Account Invoice Refund Reason.",
    'category': 'Accounting',
    'author':
        "Open Source Integrators, "
        "Serpent CS, "
        "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-invoicing',
    'data': [
        'security/ir.model.access.csv',
        'data/account.invoice.refund.reason.csv',
        'views/account_invoice_view.xml',
        'views/account_invoice_refund_reason_view.xml',
        'wizard/account_invoice_refund_view.xml'],
    'depends': ['account'],
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['max3903'],
}
