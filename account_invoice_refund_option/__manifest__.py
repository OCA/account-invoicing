# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
{
    "name": "Account Invoice Refund Option",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "Account Invoice Refund Option",
    "author": "La Louve, Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_move_reversal_view.xml",
        "views/account_move_view.xml",
    ],
    "installable": True,
}
