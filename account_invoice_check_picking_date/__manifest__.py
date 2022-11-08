# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Invoice Check Picking Date",
    "summary": "Check if date of pickings match with invoice date",
    "version": "14.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_account"],
    "maintainers": ["carlosdauden"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/invoice_stock_picking_date_wiz.xml",
    ],
}
