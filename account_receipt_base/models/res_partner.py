#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.convert import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_receipts = fields.Boolean()
    total_receipts_invoiced = fields.Monetary(
        compute="_compute_total_receipts_invoiced",
        string="Total Receipts Invoiced",
        groups="account.group_account_invoice,account.group_account_readonly",
    )

    def _compute_total_receipts_invoiced(self):
        # Similar to res.partner._invoice_total,
        # only the filtered move_type is changed
        partner_to_children_dict = {}
        all_partners = self
        for partner in self:
            child_partners = self.search(
                [
                    ("id", "child_of", partner.id),
                ]
            )
            partner_to_children_dict[partner] = child_partners
            all_partners |= child_partners

        domain = [
            ("partner_id", "in", all_partners.ids),
            ("state", "not in", ["draft", "cancel"]),
            ("move_type", "=", "out_receipt"),  # This changed
        ]
        price_totals = self.env["account.invoice.report"].read_group(
            domain,
            ["price_subtotal"],
            ["partner_id"],
        )

        for partner, children in partner_to_children_dict.items():
            partner.total_receipts_invoiced = sum(
                price["price_subtotal"]
                for price in price_totals
                if price["partner_id"][0] in children.ids
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
