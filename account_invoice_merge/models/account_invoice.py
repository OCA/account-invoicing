# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from itertools import groupby
from operator import attrgetter

from odoo import api, models
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def link_analytic_lines(self):
        """Link analytic lines from the old invoices to the new one.
        """
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        if 'invoice_id' in analytic_line_obj._fields:
            analytic_todos = analytic_line_obj.search(
                [('invoice_id', '=', self.id)]
            )
            analytic_todos.write({'invoice_id': self.id})

    @api.multi
    def link_sale_orders(self, old_invoices):
        """Link sale order lines from the old invoices to the new one.

        If sale module is installed.
        """
        self.ensure_one()
        invoice_line_obj = self.env['account.invoice.line']
        if 'sale.order' in self.env.registry:
            sale_todos = old_invoices.mapped(
                'invoice_line_ids.sale_line_ids.order_id'
            )
            for original_so in sale_todos:
                for so_line in original_so.order_line:
                    invoice_line = invoice_line_obj.search([
                        ('id', 'in', so_line.invoice_lines.ids),
                        ('invoice_id', '=', self.id)
                    ])
                    if invoice_line:
                        so_line.write({
                            'invoice_lines': [(6, 0, invoice_line.ids)]
                        })

    @api.model
    def _get_invoice_group_fields(self):
        """Fields that invoices are getting grouped upon.

        This are the fields that will be carried over from the old invoices
        to the new one. Content of this fields should be strictly equal for
        the invoices to be merged.
        """
        return [
            'partner_id',
            'user_id',
            'type',
            'account_id',
            'currency_id',
            'journal_id',
            'company_id',
            'partner_bank_id',
        ]

    @api.multi
    def get_group_values(self):
        """Calculate values for grouping.
        """
        self.ensure_one()
        group_dict = {}
        for field in self._get_invoice_group_fields():
            value = getattr(self, field)
            field_type = self.fields_get()[field]['type']
            if field_type == 'many2one':
                value = value.id
            elif field_type == 'many2many':
                value = [(4, x.id) for x in value]
            elif field_type == 'one2many':
                value = [(6, 0, value.ids)]
            group_dict[field] = value
        return group_dict

    @api.multi
    def group_by_fields(self):
        """Groups invoices by their fields values.

        Takes invoices and then groups them by their values from
        get_group_values() fields. Returns list of recordsets.
        """
        groups = []
        for key, group in groupby(
                self.sorted(key=attrgetter(*self._get_invoice_group_fields())),
                key=lambda x: x.get_group_values(),
        ):
            recordset = self.env["account.invoice"]
            for record in group:
                recordset |= record
            groups.append(recordset)
        return groups

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False,
                 remove_empty_invoice_lines=True):
        """Merge invoices.

        Groups invoices by their fields values and then creates a new
        merge invoice, while cancelling old ones.
        :param keep_references: Boolean, if True, new invoice name will
                                contain names of the merged invoices.
        :param date_invoice: Date, if not False, will fill date_invoice
                             field with passed values
        :param remove_empty_invoice: Boolean, if True, will ignore invoice
                                     lines with quantity=0
        :return: dict, keys are new invoice id, and values being ids of old
                 invoices
        """
        qty_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        # we only work with draft invoices. We have a dirty check for
        # this in wizard as well
        draft_invoices = self.filtered(lambda x: x.state == 'draft')
        grouped_invoices = draft_invoices.group_by_fields()
        result = {}
        for group in grouped_invoices:
            # Ignore groups of 1 invoice as there is nothing to merge there
            if len(group) < 2:
                continue
            # Building values for the new invoice
            # As this values are the same across the group
            # we can simply take them from the first invoice of the group
            vals = group[0].get_group_values()
            if keep_references:
                vals['name'] = " ".join(
                    (x for x in group.mapped("name") if x)
                )
            if date_invoice:
                vals["date_invoice"] = date_invoice
            vals.update({
                'origin': " ".join(
                    (x for x in group.mapped("origin") if x)
                ),
                'reference': " ".join(
                    (x for x in group.mapped("reference") if x)
                ),
            })
            lines = []
            # merge invoice lines
            line_ids = group.mapped("invoice_line_ids")
            for line_group in line_ids.group_by_fields():
                line_vals = line_group[0].get_group_values()
                line_vals['quantity'] = sum(line_group.mapped('quantity'))
                if remove_empty_invoice_lines:
                    # TODO: not sure this check is needed as
                    # I don't see the case when this is 0. But
                    # just in case i copy it from original
                    if not float_is_zero(
                            line_vals['quantity'], precision_digits=qty_prec
                    ):
                        lines.append((0, 0, line_vals))
                else:
                    lines.append((0, 0, line_vals))
            vals['invoice_line_ids'] = lines
            # create new invoice
            new_invoice = self.with_context(is_merge=True).create(vals)
            # cancel old invoices
            group.with_context(is_merge=True).action_invoice_cancel()
            # link sale orders from old invoices
            new_invoice.link_sale_orders(group)
            # link analytic lines from old invoices
            new_invoice.link_analytic_lines()
            # recompute taxes
            new_invoice.compute_taxes()
            result[new_invoice.id] = group.ids
        return result
