# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Order Partner",
    "summary": "Add order partner to invoices and print it on the report",
    "category": "Invoice",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "reports/report_invoice_document.xml",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
