# Copyright 2019 Eficent Business and IT Consulting Services
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Picking Return Invoicing",
    "summary": "Add an option to refund returned pickings",
    "version": "13.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Eficent," "Tecnativa," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Mature",
    "depends": ["purchase_stock"],
    "data": ["views/account_invoice_view.xml", "views/purchase_view.xml"],
    "maintainers": ["pedrobaeza"],
}
