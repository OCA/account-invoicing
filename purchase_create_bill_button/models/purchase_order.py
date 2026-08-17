# Copyright 2026 Juan Arcos MTS <j.arcos@madetosoft.com>
# Copyright 2026 Oriol Gracia MTS <o.gracia@madetosoft.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools import groupby
from odoo.tools.float_utils import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self, attachment_ids=False):
        precision = self.env["decimal.precision"].precision_get("Product Unit")

        invoice_vals_list = []
        sequence = 10
        for order in self:
            order = order.with_company(order.company_id)
            pending_section = None
            invoice_vals = order._prepare_invoice()
            for line in order.order_line:
                if line.display_type in ("line_section", "line_subsection"):
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({"sequence": sequence})
                        invoice_vals["invoice_line_ids"].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({"sequence": sequence})
                    invoice_vals["invoice_line_ids"].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        new_invoice_vals_list = []
        for _grouping_keys, invoices in groupby(
            invoice_vals_list,
            key=lambda x: (
                x.get("company_id"),
                x.get("partner_id"),
                x.get("currency_id"),
            ),
        ):
            origins = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals["invoice_line_ids"] += invoice_vals[
                        "invoice_line_ids"
                    ]
                origins.add(invoice_vals["invoice_origin"])
            ref_invoice_vals.update({"invoice_origin": ", ".join(origins)})
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        invoices = self.env["account.move"]
        AccountMove = self.env["account.move"].with_context(
            default_move_type="in_invoice"
        )
        for vals in invoice_vals_list:
            invoices |= AccountMove.with_company(vals["company_id"]).create(vals)

        invoices.filtered(
            lambda m: m.currency_id.round(m.amount_total) < 0
        ).action_switch_move_type()

        attachments = self.env["ir.attachment"].browse(attachment_ids)
        if not attachments:
            return self.action_view_invoice(invoices)

        if len(invoices) != 1:
            raise ValidationError(
                self.env._("You can only upload a bill for a single vendor at a time.")
            )
        invoices.with_context(skip_is_manually_modified=True)._extend_with_attachments(
            invoices._to_files_data(attachments),
            new=True,
        )

        invoices.message_post(attachment_ids=attachments.ids)

        attachments.write({"res_model": "account.move", "res_id": invoices.id})
        return self.action_view_invoice(invoices)
