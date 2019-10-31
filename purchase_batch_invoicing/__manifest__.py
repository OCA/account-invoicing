# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Batch Invoicing",
    "summary": "Make invoices for all ready purchase orders",
    "version": "12.0.1.0.0",
    "category": "Purchases",
    "website": "https://www.github.com/OCA/account-invoicing",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "wizards/purchase_batch_invoicing_view.xml",
        "views/purchase_order_view.xml",
    ],
    "images": [
        "static/description/wizard.png",
    ],
}
