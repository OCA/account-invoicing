# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'
   
    split = fields.Boolean(string='Split')
    state = fields.Selection(related='invoice_id.state')
    

	

