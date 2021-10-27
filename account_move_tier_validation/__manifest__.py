# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Move Tier Validation",
    "summary": "Extends the functionality of Account Moves to "
    "support a tier validation process.",
    "version": "14.0.1.0.1",
    "category": "Accounts",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "base_tier_validation"],
    "data": [
        "data/mail_template_data.xml",
        "security/ir.model.access.csv",
        "views/account_move_view.xml",
        "views/tier_definition_view.xml",
        "wizard/account_invoice_validation_send.xml",
    ],
}
