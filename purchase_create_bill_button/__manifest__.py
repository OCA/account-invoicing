# Copyright 2026 Juan Arcos MTS <j.arcos@madetosoft.com>
# Copyright 2026 Oriol Gracia MTS <o.gracia@madetosoft.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Create Bill Button",
    "summary": "Add a direct button to create bills from purchase orders",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Madetosoft, Odoo Community Association (OCA)",
    "maintainers": ["jarcosmts", "ograciamts"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": ["views/purchase_order_views.xml"],
}
