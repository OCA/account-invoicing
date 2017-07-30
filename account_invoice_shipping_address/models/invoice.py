# -*- coding: utf-8 -*-

from openerp import fields, models

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    address_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string ='Shipping Address',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        help="Delivery address for current invoice.")
    
