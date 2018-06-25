# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Pro forma invoice sequence",
    "summary": "Bind a sequence to pro-forma invoices",
    "version": "10.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing/tree/10.0/"
               "account_invoice_pro_forma_sequence",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account.xml",
        "views/account_config_settings.xml"
    ]
}
