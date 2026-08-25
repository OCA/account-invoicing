# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_last_completed_picking(self):
        self.ensure_one()
        return self.picking_ids.filtered(lambda p: p.state == "done").sorted(
            key=lambda p: p.date_done, reverse=True
        )[:1]

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        date_field = self.company_id.picking_date_field_for_invoice_date.sudo()
        if not date_field:
            return invoice_vals
        picking = self._get_last_completed_picking()
        if not picking:
            return invoice_vals
        date_value = getattr(picking, date_field.name, False)
        if date_field.ttype == "date" and date_value:
            invoice_vals["invoice_date"] = date_value
        else:
            tz = self.company_id.partner_id.tz or self.env.user.tz
            invoice_vals["invoice_date"] = fields.Datetime.context_timestamp(
                self.with_context(tz=tz),
                date_value or picking.date_done,
            ).date()
        return invoice_vals
