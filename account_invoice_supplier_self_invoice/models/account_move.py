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
        readonly=False,
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
            if move.is_purchase_document(False) or not (
                move.ref and move.self_invoice_number
            ):
                continue
            if move.ref != move.self_invoice_number:
                move.is_self_invoice_number_different = True

    @api.depends("partner_id", "move_type")
    def _compute_self_invoice(self):
        """Inherit default for self-invoice from partner."""
        for move in self:
            partner_self_invoice = (
                move.is_purchase_document(False)
                and move.with_company(
                    move.company_id or self.env.company,
                ).partner_id.commercial_partner_id.self_invoice
            )
            move.set_self_invoice = partner_self_invoice
            move.can_self_invoice = partner_self_invoice

    def _post(self, soft=True):
        # Set today for invoice date in self invoices
        self.filtered(
            lambda inv: inv.is_purchase_document(False)
            and inv.set_self_invoice
            and not inv.invoice_date
        ).invoice_date = fields.Date.today()
        res = super()._post(soft=soft)
        for invoice in self:
            partner = invoice.with_company(
                invoice.company_id or self.env.company,
            ).partner_id.commercial_partner_id
            if (
                partner.self_invoice
                and invoice.is_purchase_document(False)
                and invoice.set_self_invoice
                and not invoice.self_invoice_number
            ):
                self_invoice_number = partner._get_self_invoice_number(invoice)
                invoice.ref = self_invoice_number
                invoice.self_invoice_number = self_invoice_number
        return res

    def _get_mail_template(self):
        """Get correct email template for self invoices"""
        if all(
            move.is_purchase_document(False) and move.self_invoice_number
            for move in self
        ):
            return "account_invoice_supplier_self_invoice.email_template_self_invoice"
        return super()._get_mail_template()
