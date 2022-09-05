# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# Copyright 2022 Simone Rubino - TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _refund_cleanup_lines(self, lines):
        result = super()._refund_cleanup_lines(lines)
        for i, line in enumerate(lines):
            for name, field in line._fields.items():
                if name == 'sale_line_ids':
                    result[i][2]['refund_sale_line_ids'] = [(6, 0, line[name].ids)]
        return result

    def _prepare_refund(
        self, invoice, date_invoice=None, date=None,
        description=None, journal_id=None,
    ):
        # Set the sale_qty_to_reinvoice based on the boolean from the
        # reversal wizard
        invoice_vals = super()._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id,
        )
        if self.env.context.get("sale_qty_to_reinvoice", False):
            for vals in invoice_vals["invoice_line_ids"]:
                vals[2].update({"sale_qty_to_reinvoice": True})
        return invoice_vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sale_qty_to_reinvoice = fields.Boolean(
        string="Sale qty to reinvoice",
        help="Leave it marked if you will reinvoice the same sale order line",
    )
    refund_sale_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='refund_sale_invoice_lines_rel',
        string="Sale Order Lines linked to this Refund Line",
    )
