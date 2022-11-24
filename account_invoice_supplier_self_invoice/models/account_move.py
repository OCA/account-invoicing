# © 2017 Creu Blanca
# Copyright 2022 - Moduon
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    self_invoice_number = fields.Char(
        string="Self-Bill Invoice Number",
        readonly=True,
        copy=False,
    )
    is_self_invoice_number_different = fields.Boolean(
        string="Different Invoice Reference and Self-Bill Invoice Number",
        compute="_compute_is_self_invoice_number_different",
        help="Self-Bill Number is different than Invoice Reference",
    )
    set_self_invoice = fields.Boolean(
        help="If enabled, create a Self-Bill Invoice when validating.",
        compute="_compute_self_invoice",
        store=True,
    )
    can_self_invoice = fields.Boolean(
        string="Approves Self Billing",
        compute="_compute_self_invoice",
        store=True,
        readonly=True,
    )

    def _compute_is_self_invoice_number_different(self):
        """Compute if ref is different than self-invoice number"""
        self.is_self_invoice_number_different = False
        for move in self:
            if move.move_type not in {"in_invoice", "in_refund"} or not (
                move.ref and move.self_invoice_number
            ):
                continue
            if move.ref != move.self_invoice_number:
                move.is_self_invoice_number_different = True

    @api.depends("partner_id", "move_type")
    def _compute_self_invoice(self):
        """Inherit default for self-invoice from partner."""
        in_move_types = {"in_invoice", "in_refund"}
        for move in self:
            partner_self_invoice = (
                move.move_type in in_move_types
                and move.with_company(
                    move.company_id or self.env.company,
                ).partner_id.self_invoice
            )
            move.set_self_invoice = partner_self_invoice
            move.can_self_invoice = partner_self_invoice

    def action_post(self):
        in_move_types = {"in_invoice", "in_refund"}
        # Set today for invoice date in self invoices
        self.filtered(
            lambda inv: inv.move_type in in_move_types
            and inv.set_self_invoice
            and not inv.invoice_date
        ).invoice_date = fields.Date.today()
        res = super().action_post()
        for invoice in self:
            partner = invoice.with_company(
                invoice.company_id or self.env.company,
            ).partner_id
            if (
                partner.self_invoice
                and invoice.move_type in in_move_types
                and invoice.set_self_invoice
                and not invoice.self_invoice_number
            ):
                sequence = partner.self_invoice_sequence_id
                invoice.self_invoice_number = sequence.with_context(
                    ir_sequence_date=invoice.date
                ).next_by_id()
                invoice.ref = invoice.self_invoice_number
        return res

    def _get_mail_template(self):
        """Get correct email template for self invoices"""
        in_move_types = {"in_invoice", "in_refund"}
        if all(
            move.move_type in in_move_types and move.self_invoice_number
            for move in self
        ):
            return "account_invoice_supplier_self_invoice.email_template_self_invoice"
        return super()._get_mail_template()
