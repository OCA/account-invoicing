# Copyright 2022 Lorenzo Battistini - TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Receipts Journals",
    "summary": "Define and use journals dedicated to receipts",
    "version": "15.0.1.0.1",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_journal_views.xml",
        "data/account_journal_data.xml",
    ],
    "pre_init_hook": "rename_old_italian_data",
    "external_dependencies": {
        "python": [
            "openupgradelib",
        ],
    },
}
