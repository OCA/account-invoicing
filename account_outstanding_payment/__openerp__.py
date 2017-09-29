# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# © 2017 Odoo SA <https://www.odoo.com>
# © 2017 OCA <https://odoo-community.org>
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.en.html).
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
