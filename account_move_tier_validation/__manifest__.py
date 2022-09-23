# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Move Tier Validation",
    "summary": "Extends the functionality of Account Moves to "
    "support a tier validation process.",
    "version": "15.0.1.1.1",
    "category": "Accounts",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "base_tier_validation"],
    "data": ["views/account_move_view.xml"],
}
