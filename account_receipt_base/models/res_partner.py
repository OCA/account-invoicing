# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.convert import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_receipts = fields.Boolean()
    total_receipts_invoiced = fields.Monetary(
        compute="_compute_total_receipts_invoiced",
        groups="account.group_account_invoice,account.group_account_readonly",
    )

    def _compute_total_receipts_invoiced(self):
        # Similar to res.partner._invoice_total,
        # only the filtered move_type is changed
        self.total_receipts_invoiced = 0
        if not self.ids:
            return

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered("id"):
            all_partners_and_children[partner] = (
                self.with_context(active_test=False)
                .search([("id", "child_of", partner.id)])
                .ids
            )
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ("partner_id", "in", all_partner_ids),
            ("state", "not in", ["draft", "cancel"]),
            ("move_type", "=", "out_receipt"),
        ]
        price_totals = self.env["account.invoice.report"]._read_group(
            domain, ["partner_id"], ["price_subtotal:sum"]
        )
        for partner, child_ids in all_partners_and_children.items():
            partner.total_receipts_invoiced = sum(
                price_subtotal_sum
                for partner, price_subtotal_sum in price_totals
                if partner.id in child_ids
            )

    def action_view_partner_receipts(self):
        # Similar to res.partner.action_view_partner_invoices,
        # only the filtered move_type is changed
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_receipt_type"
        )
        all_child = self.with_context(active_test=False).search(
            [("id", "child_of", self.ids)]
        )

        action_domain_str = action.get("domain")
        if action_domain_str is not None:
            action_domain = safe_eval(action_domain_str)
        else:
            action_domain = []

        action["domain"] = expression.AND(
            (
                action_domain,
                [
                    ("partner_id", "in", all_child.ids),
                ],
            )
        )
        return action

    @api.onchange("use_receipts")
    def onchange_use_receipts(self):
        if self.use_receipts:
            # Partner is receipts, assign a receipts
            # fiscal position only if there is none
            if not self.property_account_position_id:
                company = self.company_id or self.env.company
                self.property_account_position_id = self.env[
                    "account.fiscal.position"
                ].get_receipts_fiscal_pos(company)
        else:
            # Unset the fiscal position only if it was receipts
            if self.property_account_position_id.receipts:
                self.property_account_position_id = False
