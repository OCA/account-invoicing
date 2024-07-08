# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchases order invoicing grouping criteria",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/purchase_invoicing_grouping_criteria_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
}
