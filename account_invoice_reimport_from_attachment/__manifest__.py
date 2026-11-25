# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Reimport From Attachment",
    "summary": """Allows re-importing invoice lines from an attached document,
    replacing existing lines.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": [
        "security/groups.xml",
        "security/account_move_reimport_attachment_wizard.xml",
        "views/account_move.xml",
        "wizards/account_move_reimport_attachment_wizard.xml",
    ],
    "demo": [],
}
