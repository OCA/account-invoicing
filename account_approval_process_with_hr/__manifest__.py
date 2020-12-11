# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account approval process with HR",
    "summary": "Account approval process for vendor bills (with HR)",
    "version": "11.0.4.0.0",
    "category": "Accounting",
    "author": "Elego Software Solutions GmbH,"
              "Odoo Community Association (OCA)",
    "depends": [
        "account_approval_process",
        "hr",
    ],
    "data": [
        "views/account_approval_process_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "auto_install": True,
    "license": "AGPL-3",
}
