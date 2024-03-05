# Copyright 2016-2022 Lorenzo Battistini
# Copyright 2018-2019 Simone Rubino
# Copyright 2019 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# Copyright 2020 Giovanni Serra - GSLab.it
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Receipts from sales",
    "summary": "Generate receipts from sale orders",
    "version": "14.0.1.0.1",
    "development_status": "Beta",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "TAKOBI, Agile Business Group, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "account_receipt_base",
        "account_receipt_journal",
        "sale",
    ],
    "data": [
        "views/sale_views.xml",
    ],
    "pre_init_hook": "rename_old_italian_module",
    "post_init_hook": "migrate_corrispettivi_data",
    "external_dependencies": {
        "python": [
            "openupgradelib",
        ],
    },
}
