# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Account Move Tier Validation Approver",
    "version": "13.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Accounting",
    "license": "LGPL-3",
    "depends": ["account_move_tier_validation"],
    "data": [
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
