# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Show links between refunds and their originator invoices",
    "version": "13.0.1.1.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Pexego, Tecnativa, Odoo Community Association (OCA)",
    "installable": True,
    "post_init_hook": "post_init_hook",
    "depends": ["account"],
    "license": "AGPL-3",
    "data": ["views/account_invoice_view.xml"],
}
