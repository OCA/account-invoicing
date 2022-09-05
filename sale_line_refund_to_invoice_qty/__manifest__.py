# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale Line Refund To Invoice Qty",
    "summary": """Allow deciding whether refunded quantity should be considered
                as quantity to reinvoice""",
    "version": "13.0.1.2.0",
    "category": "Sales",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management"],
    "data": [
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
        "wizards/account_move_reversal_view.xml",
    ],
}
