# Copyright 2022 - Akretion Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Invoicing Grouping Criteria",
    "version": "14.0.1.0.1",
    "category": "Contract",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["contract"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/contract_invoicing_grouping_criteria_views.xml",
    ],
    "installable": True,
}
