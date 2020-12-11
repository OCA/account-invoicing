# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account approval process",
    "summary": "Account approval process",
    "version": "11.0.4.0.0",
    "category": "Accounting",
    "author": "Elego Software Solutions GmbH,"
              "Odoo Community Association (OCA)",
    "depends": [
        "account",
    ],
    "data": [
        "security/security.xml",
        "views/account_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_views.xml",
        "views/account_invoice_view.xml",
        "views/account_approval_process_view.xml",
        "data/mail_template.data.xml",
    ],
    "demo": [],
    "qweb": [],
    "auto_install": False,
    "license": "AGPL-3",
}
