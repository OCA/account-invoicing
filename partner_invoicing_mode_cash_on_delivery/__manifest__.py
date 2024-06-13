# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Invoicing Mode Cash on Delivery",
    "summary": """This module allows users to distinguish cash on delivery invoices
    in the automatic invoicing flow""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "BCIM, ACSONE SA/NV, Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "account_payment_sale",
        "partner_invoicing_mode_at_shipping",
    ],
    "data": [
        "views/account_payment_mode_views.xml",
        "views/stock_picking_views.xml",
    ],
}
