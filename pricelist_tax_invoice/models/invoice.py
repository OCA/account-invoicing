# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from collections import defaultdict
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):                                                                                                                           
     _inherit = 'account.invoice.line'                                                                                                                              

     def _onchange_product_id_account_invoice_pricelist(self):                                                                                                      
         super(AccountInvoiceLine,                                                                                                                                  
                 self)._onchange_product_id_account_invoice_pricelist()                                                                                             
         print 'a'
