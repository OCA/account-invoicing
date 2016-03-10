# -*- coding: utf-8 -*-
# © 2010-2011 Ian Li <ian.li@elico-corp.com>
# © 2015 Cédric Pigeon <cedric.pigeon@acsone.eu>
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Merge Wizard',
    'version': '8.0.2.0.0',
    'category': 'Finance',
    'author': "Elico Corp, "
              "ACSONE A/V, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.openerp.net.cn',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'installable': True,
}
