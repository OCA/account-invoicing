# Copyright 2025, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Advance Compensation",
    "version": "18.0.1.0.0",
    "category": "Accounting/Invoicing",
    "summary": "Compensate advance payments from invoices",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_journal.xml",
        "views/account_move.xml",
        "wizard/compensation_wizard.xml",
    ],
}
