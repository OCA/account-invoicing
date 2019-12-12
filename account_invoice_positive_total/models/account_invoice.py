# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, models, _
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _ensure_total_is_positive(self):
        """
        Ensure the total of each invoice (self) is positive
        :return: bool
        """
        precision = self.env['decimal.precision'].precision_get('Account')
        neg_invoices = self.filtered(
            lambda r:
            r.type in ('out_invoice', 'out_refund') and
            float_compare(r.amount_total, 0, precision_digits=precision) < 0)
        if neg_invoices:
            details = "- \n".join(neg_invoices.mapped("display_name"))
            message = _("You're not allowed to validate a negative "
                        "invoice/refund:\n- %s") % details
            raise exceptions.ValidationError(message)
        return True

    @api.multi
    def action_invoice_open(self):
        """
        Inherit to ensure total are positives
        :return: bool
        """
        self._ensure_total_is_positive()
        return super(AccountInvoice, self).action_invoice_open()
