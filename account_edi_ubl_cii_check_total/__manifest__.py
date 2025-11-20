# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Edi Ubl Cii Check Total",
    "summary": """This addon extends the UBL invoice import process to automatically
    populate the suppliers check total field based on the value found in the
    XML file.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Acsone SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account_edi_ubl_cii",
        "account_invoice_check_total",
    ],
    "data": [],
    "demo": [],
}
