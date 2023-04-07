# -*- coding: utf-8 -*-
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveApplyTaxChange(models.TransientModel):
    _name = "account.move.apply.tax.change"
    _description = "Apply a tax change on invoices."

    @api.model
    def default_get(self, fields_list):
        res = super(AccountMoveApplyTaxChange, self).default_get(fields_list)
        active_model = self.env.context.get("active_model")
        if active_model == "account.invoice":
            invoice_ids = self.env.context.get("active_ids")
            self._check_invoices(invoice_ids)
            res["invoice_ids"] = [(6, 0, invoice_ids)]
        return res

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )
    tax_change_id = fields.Many2one(
        comodel_name="account.tax.change",
        ondelete="cascade",
        required=True,
        string="Tax Change",
        domain="[('company_id', '=', company_id)]",
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.invoice",
        required=True,
        string="Invoices",
        domain=(
            "[('state', 'in', ('draft', 'proforma', 'proforma2')),"
            " ('company_id', '=', company_id),"
            "]"
        ),
    )

    def _check_invoices(self, invoice_ids):
        invoices = self.env["account.invoice"].search(
            [
                ("id", "in", invoice_ids),
                ("state", "not in", ("draft", "proforma", "proforma2")),
            ]
        )
        if invoices:
            raise UserError(
                _(
                    "Unable to update taxes on the following invoices:\n\n- "
                    + "\n- ".join(invoices.mapped("name"))
                    + "\n\nThese invoices could be already paid, posted or "
                    "cancelled."
                )
            )

    @api.multi
    def validate(self):
        """Apply the tax changes on the selected invoices."""
        self.ensure_one()
        src_taxes = self.tax_change_id.mapped("change_line_ids.tax_src_id")
        self._check_invoices(self.invoice_ids.ids)
        for invoice in self.invoice_ids:
            if self._skip_invoice(invoice):
                continue
            invoice_lines = invoice.invoice_line_ids
            for line in invoice_lines:
                # Skip the line if:
                # - no tax to replace
                if not line.invoice_line_tax_ids & src_taxes:
                    continue
                # - invoice date doesn't match
                if self._skip_line(line):
                    continue
                self._change_taxes(line)
        return True

    def _skip_invoice(self, invoice):
        """No tax change on invoice already posted or paid."""
        # FIXME: this method does nothing now we have '_check_invoices'
        return invoice.state in ("open", "paid", "cancel")

    def _skip_line(self, line):
        """Return `True` if the tax change should not be applied on the line.

        Other modules could override this method.
        """
        return False

    def _change_taxes(self, line):
        """Apply the tax change in the invoice line.

        Other modules could override this method.
        """
        for tax_change_line in self.tax_change_id.change_line_ids:
            if tax_change_line.tax_src_id in line.invoice_line_tax_ids:
                line.invoice_line_tax_ids -= tax_change_line.tax_src_id
                line.invoice_line_tax_ids |= tax_change_line.tax_dest_id
        line.invalidate_cache()
        line.modified(["invoice_line_tax_ids"])
        line.recompute()
        line.invoice_id.compute_taxes()
