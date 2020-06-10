# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id_account_invoice_pricelist(self):
        result = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id and self.type in ('out_invoice', 'out_refund')\
                and self.partner_id.property_product_pricelist:
            self.pricelist_id = self.partner_id.property_product_pricelist
        return result   
    
    def button_update_prices_from_pricelist(self):
        for inv in self.filtered(lambda r: r.state == 'draft'):
            inv.invoice_line_ids.update_from_pricelist()
        self.filtered(lambda r: r.state == 'draft').with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
        self.filtered(lambda r: r.state == 'draft').with_context(check_move_validity=False)._recompute_tax_lines()   
            
       
    def _reverse_move_vals(self, default_values, cancel=True):
        """Pricelist should also be set on refund."""
        move_vals = super(AccountMove, self)._reverse_move_vals(default_values, cancel=cancel)
        if self.pricelist_id:
            move_vals['pricelist_id'] = self.pricelist_id.id
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id', 'quantity', 'product_uom_id')
    def _onchange_product_id_account_invoice_pricelist(self):
        if not self.move_id.pricelist_id or not self.move_id.partner_id:
            return
        product = self.product_id.with_context(
            lang=self.move_id.partner_id.lang,
            partner=self.move_id.partner_id.id,
            quantity=self.quantity,
            date_order=self.move_id.invoice_date,
            pricelist=self.move_id.pricelist_id.id,
            product_uom_id=self.product_uom_id.id,
            fiscal_position=(self.move_id.partner_id.property_account_position_id.id)
        )
        tax_obj = self.env['account.tax']
        list_price =  tax_obj._fix_tax_included_price_company(
            product.price,
            product.taxes_id, 
            self.tax_ids,
            self.company_id)

        self.with_context(check_move_validity=False).update({'price_unit' : list_price})
    
    
    def update_from_pricelist(self):
        """overwrite current prices from pricelist"""
        for line in self.filtered(lambda r: r.move_id.state == 'draft'):
            line._onchange_product_id_account_invoice_pricelist()
