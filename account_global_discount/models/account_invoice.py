# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    global_discount_ids = fields.Many2many(
        comodel_name='global.discount',
        column1='invoice_id',
        column2='global_discount_id',
        string='Invoice Global Discounts',
        domain="[('discount_scope', 'in', {"
               "    'out_invoice': ['sale'], "
               "    'out_refund': ['sale'], "
               "    'in_refund': ['purchase'], "
               "    'in_invoice': ['purchase']"
               "}.get(type, [])), ('account_id', '!=', False), '|', "
               "('company_id', '=', company_id), ('company_id', '=', False)]",
    )
    amount_global_discount = fields.Monetary(
        string='Total Global Discounts',
        compute='_compute_amount',
        currency_field='currency_id',
        readonly=True,
    )
    amount_untaxed_before_global_discounts = fields.Monetary(
        string='Amount Untaxed Before Discounts',
        compute='_compute_amount',
        currency_field='currency_id',
        readonly=True,
    )
    invoice_global_discount_ids = fields.One2many(
        comodel_name='account.invoice.global.discount',
        inverse_name='invoice_id',
        readonly=True,
    )

    def _set_global_discounts_by_tax(self):
        """Create invoice global discount lines by taxes combinations and
        discounts.
        """
        self.ensure_one()
        if not self.global_discount_ids:
            return
        invoice_global_discounts = self.env['account.invoice.global.discount']
        taxes_keys = {}
        # Perform a sanity check for discarding cases that will lead to
        # incorrect data in discounts
        for inv_line in self.invoice_line_ids:
            if not inv_line.invoice_line_tax_ids:
                raise exceptions.UserError(_(
                    "With global discounts, taxes in lines are required."
                ))
            for key in taxes_keys:
                if key == inv_line.invoice_line_tax_ids:
                    break
                elif key & inv_line.invoice_line_tax_ids:
                    raise exceptions.UserError(_(
                        "Incompatible taxes found for global discounts."
                    ))
            else:
                taxes_keys[inv_line.invoice_line_tax_ids] = True
        for tax_line in self.tax_line_ids:
            key = []
            to_create = True
            for key in taxes_keys:
                if tax_line.tax_id in key:
                    to_create = taxes_keys[key]
                    taxes_keys[key] = False  # mark for not duplicating
                    break  # we leave in key variable the proper taxes value
            if not to_create:
                continue
            base = tax_line.base_before_global_discounts or tax_line.base
            for global_discount in self.global_discount_ids:
                discount = global_discount._get_global_discount_vals(base)
                invoice_global_discounts += invoice_global_discounts.new({
                    'name': global_discount.display_name,
                    'invoice_id': self.id,
                    'global_discount_id': global_discount.id,
                    'discount': global_discount.discount,
                    'base': base,
                    'base_discounted': discount['base_discounted'],
                    'account_id': global_discount.account_id.id,
                    'tax_ids': [(4, x.id) for x in key],
                })
                base = discount['base_discounted']
        self.invoice_global_discount_ids = invoice_global_discounts

    def _set_global_discounts(self):
        """Get global discounts in order and apply them in chain. They will be
        fetched in their sequence order """
        for inv in self:
            inv._set_global_discounts_by_tax()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        res = super()._onchange_invoice_line_ids()
        self._set_global_discounts()
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        if (self.type in ['out_invoice', 'out_refund'] and
                self.partner_id.customer_global_discount_ids):
            self.global_discount_ids = (
                self.partner_id.customer_global_discount_ids)
        elif (self.type in ['in_refund', 'in_invoice'] and
                self.partner_id.supplier_global_discount_ids):
            self.global_discount_ids = (
                self.partner_id.supplier_global_discount_ids)
        return res

    @api.onchange('global_discount_ids')
    def _onchange_global_discount_ids(self):
        """Trigger global discount lines to recompute all"""
        return self._onchange_invoice_line_ids()

    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount',
                 'tax_line_ids.amount_rounding', 'currency_id', 'company_id',
                 'date_invoice', 'type',
                 'invoice_global_discount_ids', 'global_discount_ids')
    def _compute_amount(self):
        super()._compute_amount()
        if not self.invoice_global_discount_ids:
            return
        round_curr = self.currency_id.round
        self.amount_global_discount = sum(
            round_curr(discount.discount_amount) * - 1
            for discount in self.invoice_global_discount_ids)
        self.amount_untaxed_before_global_discounts = self.amount_untaxed
        self.amount_untaxed = (
            self.amount_untaxed + self.amount_global_discount)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if (self.currency_id and self.company_id and
                self.currency_id != self.company_id.currency_id):
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(
                self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(
                self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    def get_taxes_values(self):
        """Override this computation for adding global discount to taxes."""
        round_curr = self.currency_id.round
        tax_grouped = super().get_taxes_values()
        for key in tax_grouped.keys():
            base = tax_grouped[key]['base']
            tax_grouped[key]['base_before_global_discounts'] = base
            amount = tax_grouped[key]['amount']
            for discount in self.global_discount_ids:
                base = discount._get_global_discount_vals(
                    base)['base_discounted']
                amount = discount._get_global_discount_vals(
                    amount)['base_discounted']
            tax_grouped[key]['base'] = round_curr(base)
            tax_grouped[key]['amount'] = round_curr(amount)
        return tax_grouped

    @api.model
    def invoice_line_move_line_get(self):
        """Append global discounts move lines"""
        res = super().invoice_line_move_line_get()
        for discount in self.invoice_global_discount_ids:
            if not discount.discount:
                continue
            # Traverse upstream result for taking existing dictionary vals
            inv_lines = self.invoice_line_ids.filtered(
                lambda x: x.invoice_line_tax_ids == discount.tax_ids)
            discount_dict = {}
            for move_line_dict in res:
                if move_line_dict.get("invl_id", 0) in inv_lines.ids:
                    discount_dict.update(move_line_dict)
            # Change needed values for the global discount
            discount_dict.update({
                'invoice_global_discount_id': discount.id,
                'type': 'global_discount',
                'name': "%s - %s" % (
                    discount.name, ", ".join(discount.tax_ids.mapped("name"))),
                'price_unit': discount.discount_amount * -1,
                'quantity': 1,
                'price': discount.discount_amount * -1,
                'account_id': discount.account_id.id,
                'account_analytic_id': discount.account_analytic_id.id,
            })
            res.append(discount_dict)
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    base_before_global_discounts = fields.Monetary(
        string='Amount Untaxed Before Discounts',
        readonly=True,
    )


class AccountInvoiceGlobalDiscount(models.Model):
    _name = "account.invoice.global.discount"
    _description = "Invoice Global Discount"

    name = fields.Char(
        string='Discount Name',
        required=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        ondelete='cascade',
        index=True,
        readonly=True,
    )
    global_discount_id = fields.Many2one(
        comodel_name='global.discount',
        string='Global Discount',
        readonly=True,
    )
    discount = fields.Float(
        string='Discount',
        readonly=True,
    )
    discount_display = fields.Char(
        compute='_compute_discount_display',
        readonly=True,
        string="Discount",
    )
    base = fields.Float(
        string='Base discounted',
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    base_discounted = fields.Float(
        string='Discounted amount',
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='invoice_id.currency_id',
        readonly=True,
    )
    discount_amount = fields.Monetary(
        string='Discounted Amount',
        compute='_compute_discount_amount',
        currency_field='currency_id',
        readonly=True,
    )
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        required=True,
        string='Account',
        domain="[('user_type_id.type', 'not in', ['receivable', 'payable'])]",
    )
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
    )
    company_id = fields.Many2one(
        related='invoice_id.company_id',
        readonly=True,
    )

    def _compute_discount_display(self):
        """Given a discount type, we need to render a different symbol"""
        for one in self:
            precision = self.env['decimal.precision'].precision_get('Discount')
            one.discount_display = '{0:.{1}f}%'.format(
                one.discount * -1, precision)

    @api.depends('base', 'base_discounted')
    def _compute_discount_amount(self):
        """Compute the amount discounted"""
        for one in self:
            one.discount_amount = one.base - one.base_discounted
