# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentModeType(models.Model):
    _inherit = 'payment.mode.type'

    zugferd_code = fields.Selection([
        ('1', 'Instrument Not Defined'),
        ('3', 'Automated Clearing House Debit'),
        ('10', 'Cash'),
        ('20', 'Cheque'),
        ('31', 'Debit Transfer'),
        ('42', 'Payment to Bank Account'),
        ('48', 'Bank Card'),
        ('49', 'Direct Debit'),
        ('97', 'Clearing Between Partners'),
        ], string='ZUGFeRD Code')
