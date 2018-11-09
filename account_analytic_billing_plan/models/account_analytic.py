# Copy'analytic.account.billing.plan'right 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.models import expression
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    billing_plan_ids = fields.One2many(
        comodel_name='account.analytic.billing.plan',
        inverse_name='analytic_account_id', string='Billing plans')
    billing_plan_count = fields.Integer(
        string='# Billing Plans', compute='_compute_billing_plan_count')

    @api.multi
    def _compute_billing_plan_count(self):
        plan_obj = self.env['account.analytic.billing.plan']
        for account in self:
            account.billing_plan_count = plan_obj.search_count(
                [('analytic_account_id', '=', account.id)])

    @api.multi
    def button_open_billing_plan(self):
        self.ensure_one()
        action = self.env.ref(
            'account_analytic_billing_plan.'
            'action_account_analytic_billing_plan')
        action_dict = action.read()[0] if action else {}
        action_dict['context'] = safe_eval(
            action_dict.get('context', '{}'))
        action_dict['context'].update(
            {'default_analytic_account_id': self.id,
             'search_default_no_invoiced': True})
        domain = expression.AND([
            [('analytic_account_id', '=', self.id)],
            safe_eval(action.domain or '[]')])
        action_dict.update({'domain': domain})
        return action_dict


class AccountAnalyticBillingPlan(models.Model):
    _name = 'account.analytic.billing.plan'
    _description = 'Billing plan'
    _rec_name = 'name'
    _order = 'estimated_billing_date,partner_id,analytic_account_id,name'

    name = fields.Char(
        string='Plan Reference', required=True, copy=False,
        readonly=True, index=True, default=lambda self: _('New'))
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account',
        required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', store=True,
        related='analytic_account_id.partner_id')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    amount = fields.Float(
        string='Amount', digits=dp.get_precision('Account'), required=True)
    estimated_billing_date = fields.Date(
        string='Estimated billing date', copy=False)
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Invoice', readonly=True,
        copy=False)
    invoice_state = fields.Selection(
        string='Invoice state', related='invoice_id.state', store=True)

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for plan in self.filtered('product_id'):
            plan.amount = plan.product_id.lst_price

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('billing.plan') or
                _('New'))
        result = super(AccountAnalyticBillingPlan, self).create(vals)
        return result

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a plan.
        """
        self.ensure_one()
        journal_id = (
            self.env['account.invoice'].default_get(['journal_id'])
            ['journal_id'])
        if not journal_id:
            raise UserError(_(
                'Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.name or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal_id,
            'currency_id':
                self.partner_id.property_product_pricelist.currency_id.id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'fiscal_position_id':
                self.partner_id.property_account_position_id.id,
            'user_id': self.partner_id.user_id.id or self.env.uid,
        }
        return invoice_vals

    @api.multi
    def action_invoice_create(self):
        invoice_obj = self.env['account.invoice']
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        for plan in self.filtered(lambda p: not p.invoice_id and p.amount):
            group_key = plan.partner_id.id
            if group_key not in invoices:
                inv_data = plan._prepare_invoice()
                invoice = invoice_obj.create(inv_data)
                references[invoice] = plan
                invoices[group_key] = invoice
                invoices_origin[group_key] = [invoice.origin]
                invoices_name[group_key] = [invoice.name]
            elif group_key in invoices:
                if plan.display_name not in invoices_origin[group_key]:
                    invoices_origin[group_key].append(plan.display_name)
                if plan.display_name not in invoices_name[group_key]:
                    invoices_name[group_key].append(plan.display_name)
            plan.invoice_line_create(invoices[group_key].id, 1.0)
            plan.invoice_id = invoices[group_key]
            if references.get(invoices.get(group_key)):
                if plan not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= plan
        for group_key in invoices:
            invoices[group_key].write({
                'name': ', '.join(invoices_name[group_key]),
                'origin': ', '.join(invoices_origin[group_key]),
            })
        if not invoices:
            raise UserError(_('There is no invoiceable billing plan.'))
        for invoice in invoices.values():
            invoice.compute_taxes()

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a billing
        plan.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = (self.product_id.property_account_income_id or
                   self.product_id.categ_id.property_account_income_categ_id)
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d)'
                  ' - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id,
                 self.product_id.categ_id.name))
        fpos = self.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)
            taxes = fpos.map_tax(
                self.product_id.taxes_id, partner=self.partner_id)
        res = {
            'name': self.display_name,
            'origin': self.display_name,
            'account_id': account.id,
            'price_unit': self.amount,
            'quantity': qty,
            'uom_id': self.product_id.uom_id.id or False,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, taxes.ids)] if fpos else False,
            'account_analytic_id': self.analytic_account_id.id,
        }
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line.
            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        invoice_lines = self.env['account.invoice.line']
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for plan in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = plan._prepare_invoice_line(qty=qty)
                vals.update({
                    'invoice_id': invoice_id,
                })
                invoice_lines |= self.env['account.invoice.line'].create(vals)
        return invoice_lines
