# -*- coding: utf-8 -*-

from openerp import models, api, fields


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        'sale.order',
        'sale_order_invoice_rel', 'invoice_id', 'order_id',
        copy=False,
        string='Sales Orders',
        readonly=True,
        help="This is the list of sale orders linked to this invoice.",
    )

    @api.multi
    def action_cancel(self):
        """ Only in invoice plan case, if any of the invoice
            is cancel, make invoice exception to sales order """
        for inv in self:
            self._cr.execute("""select max(order_id) from sale_order_invoice_rel
                                where invoice_id=%s""", (inv.id,))
            order_id = self._cr.fetchone()[0] or False
            if order_id:
                order_inst = self.env['workflow.instance'].search(
                    [('res_type', '=', 'sale.order'),
                     ('res_id', '=', order_id)])
                order_witem = self.env['workflow.workitem'].search(
                    [('inst_id', '=', order_inst.id)])[0]
                inv_inst = self.env['workflow.instance'].search(
                    [('res_type', '=', 'account.invoice'),
                     ('res_id', '=', inv.id)])
                order_witem.subflow_id = inv_inst.id
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
