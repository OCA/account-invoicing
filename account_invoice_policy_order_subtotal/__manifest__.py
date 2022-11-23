# Copyright 2022 Camptocamp SA <telmo.santos@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Invoicice Policy Order Subtotal",
    "summary": """
        Invoice policy based on sale order line subtotal""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["sale_management"],
    "data": [
        "views/sale_order_views.xml",
    ],
}
