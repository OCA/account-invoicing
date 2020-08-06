# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models, _
from datetime import datetime
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_invoice_send_mail = fields.Datetime(
        string='Date invoice send mail'
    )

    def account_invoice_auto_send_mail_item_real(self, mail_template_id, author_id):
        self.ensure_one()
        _logger.info(
            _('Operations account_invoice_auto_send_mail_item_real invoice %s')
            % self.id
        )
        vals = {
            'author_id': self.user_id.partner_id.id,
            'record_name': self.number,
        }
        # Author_id (journal_id)
        if author_id:
            vals['author_id'] = author_id.id

        mail_compose_message_obj = self.env['mail.compose.message'].sudo().create(vals)
        res = mail_compose_message_obj.onchange_template_id(
            mail_template_id.id,
            'comment',
            'account.invoice',
            self.id
        )
        vals = {
            'author_id': vals['author_id'],
            'template_id': mail_template_id.id,
            'composition_mode': 'comment',
            'model': 'account.invoice',
            'res_id': self.id,
            'body': res['value']['body'],
            'subject': res['value']['subject'],
            'email_from': res['value']['email_from'],
            'record_name': self.number,
            'no_auto_thread': False,
        }
        # attachment_ids
        if 'attachment_ids' in res['value']:
            vals['attachment_ids'] = res['value']['attachment_ids']
        # update
        mail_compose_message_obj.update(vals)
        # send_mail_action
        mail_compose_message_obj.send_mail()
        # other
        self.date_invoice_send_mail = datetime.today()

    def cron_account_invoice_auto_send_mail_item(self):
        self.ensure_one()
        if self.type in ['out_invoice', 'out_refund'] \
                and not self.date_invoice_send_mail \
                and self.state in ['open', 'paid']:
            c_date = fields.Date.context_today(self)
            days_difference = (c_date - fields.Date.from_string(
                self.date_invoice
            )).days
            # send_invoice
            send_invoice = False
            if self.state == 'paid':
                send_invoice = True
            else:
                if days_difference >= self.journal_id.invoice_mail_days:
                    send_invoice = True
            # send_invoice
            if send_invoice:
                self.account_invoice_auto_send_mail_item_real(
                    self.journal_id.invoice_mail_template_id,
                    self.journal_id.invoice_mail_author_id.partner_id
                )

    @api.model
    def cron_account_invoice_auto_send_mail(self):
        invoices = self.env['account.invoice'].search(
            [
                ('state', 'in', ('open', 'paid')),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('journal_id.invoice_mail_template_id', '!=', False),
                ('date_invoice_send_mail', '=', False)
            ],
            order="date_invoice asc",
            limit=200
        )
        if invoices:
            count = 0
            for invoice in invoices:
                count += 1
                # cron_account_invoice_auto_send_mail_item
                invoice.cron_account_invoice_auto_send_mail_item()
                # logger_percent
                percent = (float(count) / float(len(invoices))) * 100
                percent = "{0:.2f}".format(percent)
                _logger.info("%s (%s / %s)" % (
                    percent,
                    count,
                    len(invoices)
                ))
