# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Account Utility Invoicing",
    "version": "18.0.1.0.0",
    "summary": "Generate customer invoices from utility usage records",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account"],
    "data": [
        "security/account_utility_security.xml",
        "security/ir.model.access.csv",
        "data/utility_invoice_sequence.xml",
        "data/decimal_precision_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_utility_menu.xml",
        "views/res_utility_type_view.xml",
        "views/res_utility_view.xml",
        "views/product_template.xml",
        "views/account_utility_views.xml",
        "views/account_move_views.xml",
    ],
    "maintainer": ["Saran440"],
}
