# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Secondary Unit",
    "summary": "Secondary unit of measure for account move lines",
    "version": "18.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Account",
    "license": "AGPL-3",
    "depends": ["account", "product_secondary_unit"],
    "data": [
        "security/account_move_secondary_unit_groups.xml",
        "report/report_invoice.xml",
        "views/account_move_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
