# Copyright 2021 Roberto Fichera <roberto.fichera@levelprime.com> Level Prime Srl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Force Invoice Origin",
    "version": "13.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Allows to force invoice origin on specific invoices",
    "author": "Level Prime Srl, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["security/security.xml", "views/account_move_view.xml"],
    "installable": True,
}
