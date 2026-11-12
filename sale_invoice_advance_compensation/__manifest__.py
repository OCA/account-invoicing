# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Advance Invoices and Compensation",
    "version": "18.0.1.0.0",
    "category": "Accounting/Invoicing",
    "summary": "Create advance invoices from payment terms and compensate later",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["sale_management", "account_invoice_advance_compensation"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_payment_term_views.xml",
        "views/res_config_settings_views.xml",
        "views/sale_advance_compensation_views.xml",
        "views/sale_order_views.xml",
        "wizards/sale_advance_payment_inv_views.xml",
        "views/account_move_views.xml",
    ],
    "demo": ["demo/sale_invoice_advance_compensation_demo.xml"],
}
