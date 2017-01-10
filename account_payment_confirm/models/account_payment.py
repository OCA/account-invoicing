# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def check_post(self):
        new_context = dict(
            self.env.context, **{'account_payment_confirm': True})
        self.with_context(new_context).post()

    @api.multi
    def post(self):
        if self.env.context.get('account_payment_confirm', False):
            for rec in self:
                error_invoices = rec.invoice_ids.filtered(
                    lambda i: i.state != 'open')
                if len(error_invoices):
                    msg = "\n".join([
                        "%s: %s - %s - %s: %s - %s" % (
                            _("invoice"), inv.partner_id.name, inv.number,
                            _("payment"), rec.name, rec.payment_date
                        ) for inv in error_invoices])
                    raise ValidationError(_(
                        """The payment cannot be processed because some """
                        """invoices are not open!\n"""
                        """%s""") % msg)
        return super(AccountPayment, self).post()
