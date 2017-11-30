# -*- coding: utf-8 -*-
# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Link refund invoice with original",
    "summary": "Link refund invoice with its original invoice",
    "version": "9.0.2.0.2",
    "category": "Accounting & Finance",
    "author": "Pexego, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "depends": [
        'account',
    ],
    "license": "AGPL-3",
    "data": [
        'views/account_invoice_view.xml',
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
