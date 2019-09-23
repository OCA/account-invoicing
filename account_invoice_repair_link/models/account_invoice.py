# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    repair_ids = fields.One2many(
        'repair.order', 'invoice_id', string='Repair Orders',
        readonly=True
    )

    def action_view_repair_orders(self):
        self.ensure_one()
        return {
            'name': _('Repair Orders'),
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.repair_ids.ids)]
        }
