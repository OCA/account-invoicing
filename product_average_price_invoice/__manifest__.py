# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Average Price From Invoices",
    "summary": "Average purchase and sale prices computed from invoices",
    "version": "17.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["eduezerouali-tecnativa"],
    "installable": True,
    "depends": ["account"],
    "data": [
        "data/ir_cron_data.xml",
        "views/res_config_settings_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
    ],
}
