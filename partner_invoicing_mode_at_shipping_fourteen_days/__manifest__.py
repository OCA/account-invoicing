# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner Invoicing Mode At Shipping Fourteen Days",
    "summary": """
        This is a glue module in order to select the correct invoices to post
        for partners that have '14 days' invoicing mode""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "maintainers": ["rousseldenis"],
    "depends": [
        "partner_invoicing_mode_fourteen_days",
        "partner_invoicing_mode_at_shipping",
    ],
    "auto_install": True,
}
