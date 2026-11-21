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

    def _get_picking_date(self, picking, date_field):
        date_value = getattr(picking, date_field.name, False)
        if date_field.ttype == "date" and date_value:
            return date_value
        tz = self.company_id.partner_id.tz or self.env.user.tz
        return fields.Datetime.context_timestamp(
            self.with_context(tz=tz),
            date_value or picking.date_done,
        ).date()

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        company = self.company_id
        invoice_date_field = company.picking_date_field_for_invoice_date.sudo()
        accounting_date_field = company.picking_date_field_for_accounting_date.sudo()
        if not invoice_date_field and not accounting_date_field:
            return invoice_vals
        picking = self._get_last_completed_picking()
        if not picking:
            return invoice_vals
        if invoice_date_field:
            invoice_vals["invoice_date"] = self._get_picking_date(
                picking, invoice_date_field
            )
        if accounting_date_field:
            invoice_vals["date"] = self._get_picking_date(
                picking, accounting_date_field
            )
        return invoice_vals
