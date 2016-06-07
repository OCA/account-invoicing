# -*- coding: utf-8 -*-
# © 2016 KMEE - Luis Felipe Mileo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    invoice_partner_id = fields.Many2one(
        'res.partner',
        string='Invoice Partner'
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_partner_to_invoice(self, picking):
        result = super(StockPicking, self)._get_partner_to_invoice(picking)
        rule_invoice_partner = False
        for procurement in picking.group_id.procurement_ids:
            rule_invoice_partner = (
                procurement.rule_id.invoice_partner_id and
                procurement.rule_id.invoice_partner_id.id or False
            )
        if rule_invoice_partner:
            return rule_invoice_partner
        return result
