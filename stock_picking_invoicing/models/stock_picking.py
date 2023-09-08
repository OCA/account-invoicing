# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = [
        _name,
        "stock.invoice.state.mixin",
    ]

    def set_to_be_invoiced(self):
        """
        Button to set Invoice State to To Be Invoice.
        """
        self._set_as_2binvoiced()
        self.mapped("move_ids")._set_as_2binvoiced()

    def set_as_invoiced(self):
        """
        Button to set Invoice State to Invoiced.
        """
        self._set_as_invoiced()
        self.mapped("move_ids")._set_as_invoiced()

    def set_as_not_billable(self):
        """
        Button to set Invoice State to Not Billable.
        """
        self._set_as_not_billable()
        self.mapped("move_ids")._set_as_not_billable()

    def _get_partner_to_invoice(self):
        self.ensure_one()
        partner = self.partner_id
        return partner.address_get(["invoice"]).get("invoice")

    def action_assign(self):
        """If any stock move is to be invoiced, picking status is updated"""
        if any(m.invoice_state == "2binvoiced" for m in self.mapped("move_ids")):
            self.write({"invoice_state": "2binvoiced"})
        return super().action_assign()

    @api.onchange("invoice_state")
    def _onchange_invoice_state(self):
        for record in self:
            record._update_invoice_state(record.invoice_state)
            record.mapped("move_ids")._update_invoice_state(record.invoice_state)
