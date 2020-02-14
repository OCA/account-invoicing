# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Move Tier Validation",
    "summary": "Extends the functionality of Account Moves to "
    "support a tier validation process.",
    "version": "13.0.1.0.0",
    "category": "Accounts",
    "website": "https://github.com/OCA/purchase-workflow",
    "contributors": ["Odoo Peru"],
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "base_tier_validation"],
    "data": ["views/account_move_view.xml"],
}
