# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Acccount Invoice Section Sale Order",
    "version": "14.0.1.1.0",
    "summary": "For invoices targetting multiple sale order add"
    "sections with sale order name.",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "sale"],
    "data": [
        "security/res_groups.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
    ],
}
