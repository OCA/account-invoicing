# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Edi No Autocreate Partner",
    "summary": """Prevents auto-creation of partners during invoice import by
    assigning unmatched invoices to a protected “Partner Not Found” contact.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account_edi"],
    "data": ["data/res_partner.xml"],
    "demo": [],
}
