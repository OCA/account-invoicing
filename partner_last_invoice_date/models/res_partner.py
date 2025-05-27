# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_invoice_date = fields.Date(
        compute="_compute_last_invoice_bill_date",
        store=True,
        recursive=True,
    )
    last_bill_date = fields.Date(
        compute="_compute_last_invoice_bill_date",
        store=True,
        recursive=True,
    )

    def _last_invoice_date_domain(self):
        self.ensure_one()
        all_child = self.with_context(active_test=False).search(
            [("id", "child_of", self.id)]
        )
        domain = [
            ("partner_id", "in", all_child.ids),
            ("state", "=", "posted"),
            ("invoice_date", "!=", False),
        ]
        return domain

    @api.depends(
        "invoice_ids.state",
        "invoice_ids.invoice_date",
        "invoice_ids.move_type",
        "child_ids.last_invoice_date",
        "child_ids.last_bill_date",
    )
    def _compute_last_invoice_bill_date(self):
        self.last_invoice_date = False
        self.last_bill_date = False
        for partner in self:
            inv_domain = partner._last_invoice_date_domain() + [
                ("move_type", "in", ("out_invoice", "out_refund"))
            ]
            bill_domain = partner._last_invoice_date_domain() + [
                ("move_type", "in", ("in_invoice", "in_refund"))
            ]
            last_inv = self.env["account.move"].search(
                inv_domain, order="invoice_date desc", limit=1
            )
            last_bill = self.env["account.move"].search(
                bill_domain, order="invoice_date desc", limit=1
            )
            partner.last_invoice_date = last_inv.invoice_date if last_inv else False
            partner.last_bill_date = last_bill.invoice_date if last_bill else False
