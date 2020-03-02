# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Transmit Method",
    "version": "13.0.1.0.0",
    "category": "Accounting/Accounting",
    "license": "AGPL-3",
    "summary": "Configure invoice transmit method (email, post, portal, ...)",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account", "base_view_inheritance_extension"],
    "data": [
        "security/ir.model.access.csv",
        "views/transmit_method.xml",
        "views/account_move.xml",
        "views/partner.xml",
        "data/transmit_method.xml",
    ],
    "demo": ["demo/partner.xml"],
    "installable": True,
}
