# Copyright 2015 Acsone
# Copyright 2018 Tecnativa - Cristina Martin R.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, field, models
from operator import attrgetter

AVAILABLE_SORT_OPTIONS = [
    ('sequence', 'Sequence'),
    ('name', 'Description'),
    ('price_unit', 'Unit Price'),
    ('price_subtotal', 'Amount'),
]
AVAILABLE_ORDER_OPTIONS = [
    ('asc', 'Ascending'),
    ('desc', 'Descending')
]


class account_invoice(models.Model):
    _inherit = "account.invoice"
    _sort_trigger_fields = ('line_order',
                            'line_order_direction')

    line_order = fields.Selection(AVAILABLE_SORT_OPTIONS,
                                  "Sort Lines By",
                                  default='sequence')
    line_order_direction = fields.Selection(AVAILABLE_ORDER_OPTIONS,
                                            "Sort Direction",
                                            default='asc')

    @api.model
    def get_partner_sort_options(self, partner_id):
        res = {}
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res['line_order'] = partner.line_order
            res['line_order_direction'] = partner.line_order_direction
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.line_order = self.partner_id.line_order
            self.line_order_direction = self.partner_id.line_order_direction

    @api.one
    def _sort_account_invoice_line(self):
        if self.invoice_line_ids:
            sequence = 0
            key = attrgetter(self.line_order)
            reverse = self.line_order_direction == 'desc'
            for line in self.invoice_line_ids.sorted(key=key, reverse=reverse):
                sequence += 10
                line.sequence = sequence

    @api.multi
    def write(self, vals):
        sort = False
        fields = [key for key in vals if key in self._sort_trigger_fields]
        if fields:
            if [key for key in fields if vals[key] != self[key]]:
                sort = True
        res = super(account_invoice, self).write(vals)
        if sort or 'invoice_line_ids' in vals:
            self._sort_account_invoice_line()
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not [key for key in vals if key in self._sort_trigger_fields]:
            partner_id = vals.get('partner_id', False)
            vals.update(self.get_partner_sort_options(partner_id))
        invoice = super(account_invoice, self).create(vals)
        invoice._sort_account_invoice_line()
        return invoice


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    _sort_trigger_fields = ('name', 'quantity', 'price_unit', 'discount')

    @api.multi
    def write(self, vals):
        sort = False
        fields = [key for key in vals if key in self._sort_trigger_fields]
        if fields:
            if [key for key in fields if vals[key] != self[key]]:
                sort = True
        res = super(account_invoice_line, self).write(vals)
        if sort:
            self.invoice_id._sort_account_invoice_line()
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        line = super(account_invoice_line, self).create(vals)
        self.invoice_id._sort_account_invoice_line()
        return line
