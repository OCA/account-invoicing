# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def _check_invoice_date(self):
        if self.filtered(lambda i: not i.date_invoice):
            raise ValidationError(
                _('You have to fill in the invoice date before validating'
                  'the invoice !')
            )

    @api.multi
    def action_invoice_open(self):
        """
        Force user to fill in the invoice date manually before validating
        the invoice
        """
        self._check_invoice_date()
        return super(AccountInvoice, self).action_invoice_open()
