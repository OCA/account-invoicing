# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models
from datetime import datetime
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_invoice_send_mail = fields.Datetime(
        string='Date invoice send mail'
    )

    @api.one
    def account_invoice_auto_send_mail_item_real(self, mail_template_id, author_id):
        _logger.info('Operations account_invoice_auto_send_mail_item_real invoice ' + str(self.id))

        mail_compose_message_vals = {
            'author_id': self.user_id.partner_id.id,
            'record_name': self.number,
        }
        # Author_id (journal_id)
        if author_id.id > 0:
            mail_compose_message_vals['author_id'] = author_id.id

        mail_compose_message_obj = self.env['mail.compose.message'].with_context().sudo().create(mail_compose_message_vals)
        return_onchange_template_id = mail_compose_message_obj.onchange_template_id(mail_template_id.id, 'comment', 'account.invoice', self.id)

        mail_compose_message_obj_vals = {
            'author_id': mail_compose_message_vals['author_id'],
            'template_id': mail_template_id.id,
            'composition_mode': 'comment',
            'model': 'account.invoice',
            'res_id': self.id,
            'body': return_onchange_template_id['value']['body'],
            'subject': return_onchange_template_id['value']['subject'],
            'email_from': return_onchange_template_id['value']['email_from'],
            'record_name': self.number,
            'no_auto_thread': False,
        }
        # attachment_ids
        if 'attachment_ids' in return_onchange_template_id['value']:
            mail_compose_message_obj_vals['attachment_ids'] = return_onchange_template_id['value']['attachment_ids']
        # update
        mail_compose_message_obj.update(mail_compose_message_obj_vals)
        # send_mail_action
        mail_compose_message_obj.send_mail_action()
        # other
        self.date_invoice_send_mail = datetime.today()

    @api.one
    def cron_account_invoice_auto_send_mail_item(self):
        if self.type in ['out_invoice', 'out_refund'] and self.date_invoice_send_mail == False and self.state in ['open', 'paid']:
            current_date = fields.Datetime.from_string(str(datetime.today().strftime("%Y-%m-%d")))
            days_difference = (current_date - fields.Datetime.from_string(self.date_invoice)).days
            # send_invoice
            send_invoice = False
            if self.state == 'paid':
                 send_invoice = True
            else:
                if days_difference >= self.journal_id.invoice_mail_days:
                    send_invoice = True
            # send_invoice
            if send_invoice:
                self.account_invoice_auto_send_mail_item_real(self.journal_id.invoice_mail_template_id, self.journal_id.invoice_mail_template_id_author_id.partner_id)

    @api.model
    def cron_account_invoice_auto_send_mail(self):
        account_invoice_ids = self.env['account.invoice'].search(
            [
                ('state', 'in', ('open', 'paid')),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('journal_id.invoice_mail_template_id', '!=', False),
                ('date_invoice_send_mail', '=', False)
             ], order="date_invoice asc", limit=200
        )
        if len(account_invoice_ids) > 0:
            count = 0
            for account_invoice_id in account_invoice_ids:
                count += 1
                # cron_account_invoice_auto_send_mail_item
                account_invoice_id.cron_account_invoice_auto_send_mail_item()
                # logger_percent
                percent = (float(count) / float(len(account_invoice_ids))) * 100
                percent = "{0:.2f}".format(percent)
                _logger.info(str(percent) + '% (' + str(count) + '/' + str(len(account_invoice_ids)) + ')')
