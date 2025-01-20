# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product From Account Move Line Link",
    "summary": """
        Adds a button on product forms to access Journal Items""",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_line_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
}
