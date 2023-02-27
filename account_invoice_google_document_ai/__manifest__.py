# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Ocr Google",
    "summary": """
        Allows to import data from document using Google Document AI""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "external_dependencies": {"python": ["google-cloud-documentai"]},
    "data": [
        "views/res_config_settings.xml",
        "views/account_move.xml",
    ],
}
