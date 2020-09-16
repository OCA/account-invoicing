# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Restocking Fee Invoicing",
    "summary": """
        On demand charge restocking fee for accepting returned goods .""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://acsone.eu/",
    "depends": ["sale", "sale_stock", "stock", "stock_account"],
    "data": [
        "data/product_product.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
        "wizards/stock_config_settings.xml",
        "wizards/stock_return_picking.xml",
    ],
    "demo": [],
}
