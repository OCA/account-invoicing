# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Invoice Tier Validation",
    "summary": "Extends the functionality of Invoice to "
    "support a tier validation process.",
    "version": "11.0.1.0.0",
    "category": "Invoices",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["account", "base_tier_validation",
                ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "demo": [
        "demo/account_invoice_tier_definition.xml",
    ],
}
