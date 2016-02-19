# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona <ainaragaldona@avanzosc.es> - Avanzosc S.L.
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock Picking Invoicing Unified",
    "version": "8.0.1.0.0",
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'AvanzOSC, '
              'Odoo Community Association (OCA)',
    'website': "http://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    'contributors': [
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>"
    ],
    "depends": ['stock_account'],
    "category": "Warehouse Management",
    "data": ['wizard/stock_invoice_onshipping_view.xml'],
    "installable": True
}
