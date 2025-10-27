# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Invoice Transmit Self Billing",
    "version": "16.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Self Billing mass sending",
    "author": "BCIM, ACSONE SA/NV, Odoo Community Association (OCA)",
    "maintainers": ["jbaudoux"],
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_transmit",
        "account_invoice_supplier_self_invoice",
    ],
    "data": [
        "views/account_move.xml",
    ],
    "installable": True,
    "auto_install": True,
}
