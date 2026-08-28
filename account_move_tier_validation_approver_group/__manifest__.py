# Copyright 2025 360ERP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Tier Validation Approver Group",
    "summary": """Account move tier validation approver""",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "author": "360 ERP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account_move_tier_validation_approver",
    ],
    "data": [
        "views/account_move.xml",
        "views/res_partner.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
