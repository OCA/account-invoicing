# © 2019 Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# © 2012-2015 SYLEAM Info Services (<http://www.syleam.fr/>)
# © 2015 Akretion (http://www.akretion.com)
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# @author: Sébastien LANGE <sebastien.lange@syleam.fr>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('invoice_id'):
            jrl = self.browse(line['invoice_id']).journal_id
            if jrl.group_invoice_lines and jrl.group_method == 'account':
                res.update({'name': '/', 'product_id': False})
        return res
