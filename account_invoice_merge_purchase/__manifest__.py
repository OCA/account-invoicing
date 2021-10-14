# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2009-2016 Noviat
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Merge Purchase",
    "summary": """Compatibility between purchase and account invoice merge""",
    "author": "ACSONE SA/NV, " "Tecnativa, " "Noviat,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Finance",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_merge",
        "purchase_stock",
    ],
    "installable": True,
}
