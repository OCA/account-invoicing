# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Qr Code Sepa Payconiq",
    "summary": """
        Allows to generate a qr code for Payconiq provider containing the url""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account_qr_code_sepa",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
}
