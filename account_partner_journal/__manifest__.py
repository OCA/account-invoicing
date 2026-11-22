# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Partner Journal",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Define default journal on partner",
    "author": "La Louve, Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
