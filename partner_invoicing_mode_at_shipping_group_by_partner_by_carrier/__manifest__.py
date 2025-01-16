# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner Invoicing Mode At Shipping Group By Partner By Carrier",
    "summary": """This module allows to take into account the non use of
    sale_id field on stock picking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "partner_invoicing_mode_at_shipping",
        "stock_picking_group_by_partner_by_carrier",
    ],
    "auto_install": True,
}
