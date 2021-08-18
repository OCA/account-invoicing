# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    self_invoice_number = fields.Char(readonly=True, copy=False)
    set_self_invoice = fields.Boolean("Set self invoice")
    can_self_invoice = fields.Boolean(related="partner_id.self_invoice")

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        self.set_self_invoice = self.partner_id.self_invoice
        return res

    def post(self):
        res = super().post()
        for invoice in self:
            partner = invoice.partner_id
            if (
                partner.self_invoice
                and invoice.type in "in_invoice"
                and invoice.set_self_invoice
            ):
                sequence = partner.self_invoice_sequence_id
                invoice.self_invoice_number = sequence.with_context(
                    ir_sequence_date=invoice.date
                ).next_by_id()
        return res

    @api.model
    def create(self, vals):
        onchanges = {
            "_onchange_partner_id": ["set_self_invoice"],
        }
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(
                            invoice[field], invoice
                        )
        return super().create(vals)

    def action_view_account_invoice_self(self):
        report = self.env["ir.actions.report"]._get_report_from_name(
            "account_invoice_supplier_self_invoice.report_invoice_self"
        )
        return report.report_action(self)
