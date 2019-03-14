# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from itertools import groupby
from operator import attrgetter

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _get_sale_fields(self):
        return [
            'sale_line_ids',
        ]

    @api.model
    def _get_invoice_line_group_fields(self):
        """Fields that invoice lines are getting grouped upon.

        This are the fields that will be carried over from the old invoice
        lines to the new one. Content of this fields should be strictly
        equal for the invoice lines to be merged.
        """
        fields = [
            'name',
            'origin',
            'discount',
            'invoice_line_tax_ids',
            'price_unit',
            'product_id',
            'account_id',
            'account_analytic_id',
            'uom_id',
            'analytic_tag_ids',
        ]
        for field in self._get_sale_fields():
            if field in self.env['account.invoice.line']._fields:
                fields.append(field)
        return fields

    @api.multi
    def get_group_values(self):
        """Calculate values for grouping.
        """
        self.ensure_one()
        group_dict = {}
        for field in self._get_invoice_line_group_fields():
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
        """Groups invoice lines by their fields values.

        Takes invoice lines and then groups them by their values from
        get_group_values() fields. Returns list of recordsets.
        """
        groups = []
        for key, group in groupby(
                self.sorted(
                    key=attrgetter(*self._get_invoice_line_group_fields())
                ),
                key=lambda x: x.get_group_values(),
        ):
            recordset = self.env["account.invoice.line"]
            for record in group:
                recordset |= record
            groups.append(recordset)
        return groups
