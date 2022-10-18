from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    receipts = fields.Boolean()

    @api.onchange('partner_id')
    def _onchange_partner_receipts_sale(self):
        self.receipts = self.partner_id.use_receipts

    @api.onchange('fiscal_position_id')
    def _onchange_fiscal_position_id_receipts(self):
        if self.fiscal_position_id:
            self.receipts = self.fiscal_position_id.receipts

    def _create_invoices(self, grouped=False, final=False, date=None):
        sale_receipts = self.filtered(lambda o: o.receipts)
        sale_no_receipts = self.filtered(lambda o: not o.receipts)
        moves = self.env["account.move"]
        if sale_receipts:
            moves |= super(SaleOrder, sale_receipts.with_context(
                force_move_type="out_receipt"
            ))._create_invoices(grouped, final, date)
        if sale_no_receipts:
            moves |= super(
                SaleOrder, sale_no_receipts
            )._create_invoices(grouped, final, date)
        return moves


class OrderLine(models.Model):
    _inherit = "sale.order.line"
