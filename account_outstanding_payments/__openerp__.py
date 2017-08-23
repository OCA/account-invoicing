# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Outstanding Payments",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Allows for reconciliation of invoices.",
    "depends": [
        'base',
        'account'
    ],
    "data": [
        'views/templates.xml',
        'views/account_invoice_view.xml',
        'views/account_config_settings_view.xml',
        'security/ir.model.access.csv',
    ],
    "qweb": [
        'static/src/xml/account_payment.xml',
    ],
    "installable": True,
}
