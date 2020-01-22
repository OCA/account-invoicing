# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase invoicing no zero line",
    "summary": "Avoid creation of zero quantity invoice lines from purchase",
    "version": "12.0.1.0.0",
    "category": "Purchase Management",
    "author": "Digital5 S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase",
    ],
    'data': [
        'views/account_journal_views.xml',
    ],
}
