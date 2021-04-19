# Copyright 2019 Creu Blanca
# Copyright 2021 FactorLibre - César Castañón <cesar.castanon@factorlibre.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    filter_refund = fields.Selection(selection_add=[('refund_lines',
                                                     "Refund specific lines")])

    line_ids = fields.Many2many(
        string="Account Invoice Refund Line",
        comodel_name='account.invoice.refund.line',
        column1='wiz_id',
        column2='line_id',
        relation='account_invoice_refund_refund_line_rel',
        domain="[('id', 'in', selectable_invoice_lines_ids)]"
    )

    selectable_invoice_lines_ids = fields.Many2many(
        comodel_name='account.invoice.refund.line',
        string='Invoice lines selectable',
    )

    @api.model
    def default_get(self, fields):
        rec = super(AccountInvoiceRefund, self).default_get(fields)
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            if 'line_ids' in fields:
                refund_line_model = self.env['account.invoice.refund.line']
                vals = self._get_vals_from_account_invoice(inv)
                line_ids = refund_line_model.create(vals)
                rec.update({
                    'selectable_invoice_lines_ids': [(6, 0, line_ids.ids)]
                })
        return rec

    def _get_vals_from_account_invoice(self, account_invoice):
        invoice_lines = account_invoice.invoice_line_ids
        lines_data = [
            {
                'name': line.name,
                'invoice_id': line.invoice_id.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'invoice_line_tax_ids': [
                    (6, 0, line.invoice_line_tax_ids.ids)
                ],
                'price_subtotal': line.price_subtotal,
                'refund_invoice_id': self.id,
                'origin_line_id': line.id
            }
            for line in invoice_lines
        ]
        return lines_data

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
                    raise UserError(_('Cannot create credit note for '
                                      'the draft/cancelled invoice.'))
                date = form.date or False
                description = form.description or inv.name
                inv_line_ids = inv.invoice_line_ids.filtered(
                    lambda l: l.id in form.line_ids.mapped(
                        'origin_line_id').sorted('id').ids
                )
                refund = inv.refund_partial(form.date_invoice, date,
                                            description, inv.journal_id.id,
                                            inv_line_ids, form.line_ids)
                created_inv.append(refund.id)

                xml_id = inv.type == \
                    'out_invoice' and 'action_invoice_out_refund' or \
                    inv.type == 'out_refund' and 'action_invoice_tree1' or \
                    inv.type == 'in_invoice' and 'action_invoice_in_refund' \
                    or inv.type == 'in_refund' and 'action_invoice_tree2'
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
