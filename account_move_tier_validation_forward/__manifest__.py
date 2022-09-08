# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Tier Validation - Forward Option",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["base_tier_validation_forward", "account_move_tier_validation"],
    "data": ["views/account_move_view.xml"],
}
