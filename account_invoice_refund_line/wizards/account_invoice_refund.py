from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    filter_refund = fields.Selection(selection_add=[('refund_lines', "Refund specific lines")])
    line_ids = fields.Many2many(string='Invoice lines to refund',
                                comodel_name='account.invoice.line', column1='wiz_id',
                                column2='line_id',
                                relation='account_invoice_line_refund_rel',
                                domain="[('id', 'in', selectable_invoice_lines_ids)]")
    selectable_invoice_lines_ids = fields.Many2many('account.invoice.line', string='Invoice lines selectable')

    @api.model
    def default_get(self, fields):
        rec = super(AccountInvoiceRefund, self).default_get(fields)
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            rec.update({'selectable_invoice_lines_ids': [(6, 0, inv.invoice_line_ids.ids)]})
        return rec

    @api.multi
    def compute_refund(self, mode='refund'):
        created_inv = []
        if mode != 'refund_lines':
            return super(AccountInvoiceRefund, self).compute_refund(mode)
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        xml_id = False
        for form in self:
            created_inv = []
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund_partial(form.date_invoice, date, description, inv.journal_id.id,
                                            form.line_ids)
                created_inv.append(refund.id)

            xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                inv.type == 'out_refund' and 'action_invoice_tree1' or \
                inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                inv.type == 'in_refund' and 'action_invoice_tree2'
            # Put the reason in the chatter
            subject = _("Credit Note")
            body = description
            refund.message_post(body=body, subject=subject)

        if xml_id:
            result = self.env.ref('account.%s' % xml_id).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True
