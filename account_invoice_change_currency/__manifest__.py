# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice - Change Currency",
    "version": "15.0.2.0.0",
    "category": "Accounting & Finance",
    "summary": "Allows to change currency of Invoice by wizard",
    "author": "Vauxoo, Komit Consulting, Odoo Community Association (OCA)",
    "maintainers": ["luisg123v", "rolandojduartem"],
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
