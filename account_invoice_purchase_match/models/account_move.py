# Copyright 2026 OSS Factory
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
#
# Functional backport of the Odoo 19.0 CE methods
# ``account.move.action_purchase_matching`` and
# ``account.move.line._add_purchase_order_lines`` (here both kept on
# ``account.move`` for simplicity, as the matching screen only ever calls
# ``_add_purchase_order_lines`` on a move):
# https://github.com/odoo/odoo/blob/19.0/addons/purchase/models/account_invoice.py
from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_purchase_matched = fields.Boolean(
        compute="_compute_is_purchase_matched",
        help="Technical: every product line of this vendor bill is already "
        "linked to a purchase order line. Used to hide the matching button.",
    )

    @api.depends("invoice_line_ids.purchase_line_id", "invoice_line_ids.display_type")
    def _compute_is_purchase_matched(self):
        for move in self:
            product_lines = move.invoice_line_ids.filtered(
                lambda line: line.display_type == "product"
            )
            move.is_purchase_matched = bool(product_lines) and all(
                line.purchase_line_id for line in product_lines
            )

    def _add_purchase_order_lines(self, purchase_order_lines):
        """Create new invoice lines from purchase order lines.

        Backport of Odoo 19.0 ``account.move._add_purchase_order_lines``. The
        19.0 version uses ``new()`` + ``invoice_line_ids +=`` inside an
        onchange env; on a persisted 16.0 draft we materialise the lines with a
        plain ``write`` (``check_move_validity=False`` so balance is only
        enforced at posting) from ``purchase.order.line._prepare_account_move_line``.
        """
        if not purchase_order_lines:
            return
        self.ensure_one()
        commands = []
        for po_line in purchase_order_lines:
            vals = po_line._prepare_account_move_line(self)
            commands.append((0, 0, vals))
        self.with_context(check_move_validity=False).write(
            {"invoice_line_ids": commands}
        )

    def action_purchase_matching(self):
        """Open the Purchase Matching screen for this vendor bill.

        Backport of Odoo 19.0 ``account.move.action_purchase_matching``.
        16.0 has no ``self.env.companies``/``child_of`` requirement for this
        single-company-aware filter, so the company filter is kept simple.
        """
        self.ensure_one()
        partner = self.partner_id | self.partner_id.commercial_partner_id
        return {
            "type": "ir.actions.act_window",
            "name": _("Purchase Matching"),
            "res_model": "purchase.bill.line.match",
            "domain": [
                ("partner_id", "in", partner.ids),
                ("company_id", "in", self.env.companies.ids),
                ("account_move_id", "in", [self.id, False]),
            ],
            "views": [
                (
                    self.env.ref(
                        "account_invoice_purchase_match.purchase_bill_line_match_tree"
                    ).id,
                    "tree",
                ),
            ],
        }
