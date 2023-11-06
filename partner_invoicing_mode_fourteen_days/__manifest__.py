# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Partner Invoicing Mode Fourteen Days",
    "version": "16.0.1.0.0",
    "summary": "Create invoices automatically on a 14 days basis (but generation each day).",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        "partner_invoicing_mode",
        "sale_stock",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings.xml",
    ],
}
