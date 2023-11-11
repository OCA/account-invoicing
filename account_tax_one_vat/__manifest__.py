# Copyright 2020 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Tax One VAT",
    "summary": "Allow only the selection of one VAT Tax.",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Acsone, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "account",
    "depends": ["account"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/account_tax_views.xml",
    ],
    "website": "https://github.com/OCA/account-invoicing",
    "installable": True,
}
