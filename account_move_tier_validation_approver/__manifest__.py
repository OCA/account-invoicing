# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Tier Validation Approver",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": ["account_move_tier_validation"],
    "website": "https://github.com/OCA/account-invoicing",
    "data": [
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
