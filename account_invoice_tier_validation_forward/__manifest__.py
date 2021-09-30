# Copyright 2021 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Tier Validation - Forward Option",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Forgeflow,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["base_tier_validation_forward", "account_invoice_tier_validation"],
    "data": ["views/account_invoice_view.xml"],
}
