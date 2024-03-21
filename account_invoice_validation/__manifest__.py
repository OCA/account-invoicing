# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Validation",
    "summary": """
        Adds a mechanism of validation on invoices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account",
    ],
    "data": [
        "views/res_partner.xml",
        "security/res_groups.xml",
        "security/account_move_note.xml",
        "views/account_move.xml",
        "views/res_config_settings.xml",
        "wizards/account_move_note.xml",
        "data/mail_template.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
}
