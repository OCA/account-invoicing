# -*- coding: utf-8 -*-
# © 2016 <OCA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools import config


JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}


JOURNAL_TYPE = [
        ('purchase_refund', 'Refund Purchase'), 
        ('purchase', 'Create Supplier Invoice'),
        ('sale_refund', 'Refund Sale'), 
        ('sale', 'Create Customer Invoice')
]

_logger = logging.getLogger(__name__)

class StockInvoiceOnshipping(models.TransientModel):
    _name = 'stock.invoice.onshipping'
    _description = "Stock Invoice Onshipping"
    
    
    #==================
    # View Parts
    #==================
    
    @api.model
    def view_init(self, fields):
        _logger.debug("VIEW init")
        context = self.env.context or {}
        
        res = super(StockInvoiceOnshipping, self).view_init(fields)
        pick_obj = self.env['stock.picking']
        count = 0
        active_ids = context.get('active_ids',[])        
        for pick in pick_obj.search([('id', 'in', active_ids)]):
            if pick.invoice_state != '2binvoiced':
                count += 1
            if not pick.partner_id :
                raise UserError(_('All your pickings must have a partner to be invoiced!'))
        if len(active_ids) == count:
            _logger.debug("Raise ")
            raise UserError(_('None of these picking require invoicing.'))
            
        
        _logger.debug("RESULT %s")
        
        return res

    
    @api.onchange('group')
    def onchange_group(self):
        self.ensure_one()
        (sale_pickings, sale_refund_pickings, purchase_pickings,
            purchase_refund_pickings) = self.get_split_pickings()
        self.show_sale_journal = bool(sale_pickings)
        self.show_sale_refund_journal = bool(sale_refund_pickings)
        self.show_purchase_journal = bool(purchase_pickings)
        self.show_purchase_refund_journal = bool(purchase_refund_pickings)
    
    
    @api.model
    def _default_journal(self, journal_type):
        company_id = self.env['res.users']._get_company()
        default_journal = self.env['account.journal'].search(
            [('type', '=', journal_type),('company_id','=', company_id )])[:1]
        return default_journal
    
    @api.model
    def _get_journal(self):
        journal_obj = self.env['account.journal']
        journal_type = self._get_journal_type()
        company_id = self.env['res.users']._get_company()
        journals = journal_obj.search([('type', '=', journal_type),('company_id','=', company_id)])   
        return journals[:1]
    
    @api.model
    def _get_journal_type(self):
        
        context = self.env.context or {}                        
        res_ids = context and context.get('active_ids', [])
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.search([('id', 'in', res_ids)])
        pick = pickings and pickings[0]
        if not pick or not pick.move_lines:
            return 'sale'
        type = pick.picking_type_id.code
        usage = pick.move_lines[0].location_id.usage if type == 'incoming' else pick.move_lines[0].location_dest_id.usage

        return JOURNAL_TYPE_MAP.get((type, usage), ['sale'])[0]
    
    #=======================
    # FIELDS
    #=======================

    journal_id = fields.Many2one(comodel_name='account.journal'
                                , string= 'Destination Journal'
                                , default = _get_journal
                                , required=False)
    journal_type = fields.Selection(JOURNAL_TYPE , 'Journal Type',
                                    default = _get_journal_type, readonly=True)
    
    group = fields.Boolean("Group by partner")
    invoice_date = fields.Date('Invoice Date')
    
    sale_journal = fields.Many2one(
        comodel_name='account.journal', string='Sale Journal',
        domain="[('type', '=', 'sale')]",
        default=lambda self: self._default_journal('sale'))
    sale_refund_journal = fields.Many2one(
        comodel_name='account.journal', string='Sale Refund Journal',
        domain="[('type', '=', 'sale_refund')]",
        default=lambda self: self._default_journal('sale_refund'))
    purchase_journal = fields.Many2one(
        comodel_name='account.journal', string='Purchase Journal',
        domain="[('type', '=', 'purchase')]",
        default=lambda self: self._default_journal('purchase'))
    purchase_refund_journal = fields.Many2one(
        comodel_name='account.journal', string="Purchase Refund Journal",
        domain="[('type', '=', 'purchase_refund')]",
        default=lambda self: self._default_journal('purchase_refund'))
    show_sale_journal = fields.Boolean(string="Show Sale Journal")
    show_sale_refund_journal = fields.Boolean(
        string="Show Refund Sale Journal")
    show_purchase_journal = fields.Boolean(string="Show Purchase Journal")
    show_purchase_refund_journal = fields.Boolean(
        string="Show Refund Purchase Journal")
        
        
    #=================
    # Business part
    #=================

    @api.multi
    def open_invoice(self):
        self.ensure_one()
        
        invoice_ids = self.create_invoice()
        if not invoice_ids:
            raise UserError(_('No invoice created!'))

        data = self.search([('id', 'in', [self[0].id])])

        action_model = False
        action = {}
        
        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice' , 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        data_pool = self.env['ir.actions.act_window']
        
        if inv_type in ["out_invoice", "out_refund"]:
            action_id = data_pool.for_xml_id('account','action_invoice_tree1')
        elif inv_type == "in_invoice":
            action_id = data_pool.for_xml_id('account','action_invoice_tree2')

        if action_id:
            action = action_id.copy()
            action['domain'] = [('id','in', invoice_ids)]
            return action
        return True

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        context = self.env.context or {}
        picking_pool = self.env['stock.picking']
        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        
        inv_type = journal2type.get(self.journal_type) or 'out_invoice'
        

        active_ids = context.get('active_ids', [])
        self = self.with_context(
                date_inv = self.invoice_date,
                inv_type = inv_type
               )

        res = picking_pool.action_invoice_create(active_ids,
              journal_id = self.journal_id.id,
              group = self.group,
              type = inv_type)
        return res

        if (config['test_enable'] and
                not self.env.context.get('test_picking_invoicing_unified')):
            return res
        self.ensure_one()
        res = []
        (sale_pickings, sale_refund_pickings, purchase_pickings,
            purchase_refund_pickings) = self.get_split_pickings()
        if sale_pickings:
            pickings = sale_pickings.with_context(
                date_inv=self.invoice_date, inv_type='out_invoice')
            res += pickings.action_invoice_create(
                journal_id=self.sale_journal.id,
                group=self.group, type='out_invoice')
        if sale_refund_pickings:
            pickings = sale_refund_pickings.with_context(
                date_inv=self.invoice_date, inv_type='out_refund')
            res += pickings.action_invoice_create(
                journal_id=self.sale_refund_journal.id,
                group=self.group, type='out_refund')
        if purchase_pickings:
            pickings = purchase_pickings.with_context(
                date_inv=self.invoice_date, inv_type='in_invoice')
            res += pickings.action_invoice_create(
                journal_id=self.purchase_journal.id,
                group=self.group, type='in_invoice')
        if purchase_refund_pickings:
            pickings = purchase_refund_pickings.with_context(
                date_inv=self.invoice_date, inv_type='in_refund')
            res += pickings.action_invoice_create(
                journal_id=self.purchase_refund_journal.id, group=self.group,
                type='in_refund')
        return res


    @api.multi
    def get_partner_sum(self, pickings, partner, inv_type, picking_type,
                        usage):
        move_obj = self.env['stock.move']
        pickings = pickings.filtered(lambda x: x.picking_type_id.code ==
                                     picking_type and x.partner_id == partner)
        if picking_type == 'outgoing':
            moves = pickings.mapped('move_lines').filtered(
                lambda x: x.location_dest_id.usage == usage)
        else:
            moves = pickings.mapped('move_lines').filtered(
                lambda x: x.location_id.usage == usage)
        return (sum([(m._get_price_unit_invoice( inv_type) *
                      m.product_uom_qty) for m in moves]),
                moves.mapped('picking_id'))

    @api.multi
    def get_split_pickings_grouped(self, pickings):
        sale_pickings = self.env['stock.picking']
        sale_refund_pickings = self.env['stock.picking']
        purchase_pickings = self.env['stock.picking']
        purchase_refund_pickings = self.env['stock.picking']

        for partner in pickings.mapped('partner_id'):
            so_sum, so_pickings = self.get_partner_sum(
                pickings, partner, 'out_invoice', 'outgoing', 'customer')
            si_sum, si_pickings = self.get_partner_sum(
                pickings, partner, 'out_invoice', 'incoming', 'customer')
            if (so_sum - si_sum) >= 0:
                sale_pickings |= (so_pickings | si_pickings)
            else:
                sale_refund_pickings |= (so_pickings | si_pickings)
            pi_sum, pi_pickings = self.get_partner_sum(
                pickings, partner, 'in_invoice', 'incoming', 'supplier')
            po_sum, po_pickings = self.get_partner_sum(
                pickings, partner, 'in_invoice', 'outgoing', 'supplier')
            if (pi_sum - po_sum) >= 0:
                purchase_pickings |= (pi_pickings | po_pickings)
            else:
                purchase_refund_pickings |= (pi_pickings | po_pickings)
        return (sale_pickings, sale_refund_pickings, purchase_pickings,
                purchase_refund_pickings)

    @api.multi
    def get_split_pickings_nogrouped(self, pickings):
        sale_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'outgoing' and
            x.move_lines[:1].location_dest_id.usage == 'customer')
        # use [:1] instead of [0] to avoid a errors on empty pickings
        sale_refund_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'incoming' and
            x.move_lines[:1].location_id.usage == 'customer')
        purchase_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'incoming' and
            x.move_lines[:1].location_id.usage == 'supplier')
        purchase_refund_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'outgoing' and
            x.move_lines[:1].location_dest_id.usage == 'supplier')
        return (sale_pickings, sale_refund_pickings, purchase_pickings,
                purchase_refund_pickings)

    @api.multi
    def get_split_pickings(self):
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.browse(self.env.context.get('active_ids', []))
        if self.group:
            return self.get_split_pickings_grouped(pickings)
        else:
            return self.get_split_pickings_nogrouped(pickings)

    