# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("partner_id", "company_id")
    def _compute_pricelist_id(self):
        res = super()._compute_pricelist_id()
        for invoice in self:
            if (
                invoice.is_sale_document()
                and invoice.line_ids.sale_line_ids.order_id.pricelist_id
            ):
                invoice.pricelist_id = (
                    invoice.line_ids.sale_line_ids.order_id.pricelist_id[0]
                )
        return res

    def action_switch_invoice_into_refund_credit_note(self):
        self = self.with_context(aml_no_recompute_price_unit=True)
        return super().action_switch_invoice_into_refund_credit_note()
