# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = [
        _name,
        "stock.invoice.state.mixin",
    ]

    def set_to_be_invoiced(self):
        """
        Update invoice_state of current pickings to "2binvoiced".
        :return: dict
        """
        self._set_as_2binvoiced()
        return {}

    def _set_as_2binvoiced(self):
        """
        Inherit to also update related moves.
        :return: bool
        """
        self.mapped("move_lines")._set_as_2binvoiced()
        return super()._set_as_2binvoiced()

    def _set_as_invoiced(self):
        """
        Inherit to also update related moves.
        :return: bool
        """
        self.mapped("move_lines")._set_as_invoiced()
        return super()._set_as_invoiced()

    def _get_partner_to_invoice(self):
        self.ensure_one()
        partner = self.partner_id
        return partner.address_get(["invoice"]).get("invoice")

    def action_assign(self):
        """If any stock move is to be invoiced, picking status is updated"""
        if any(m.invoice_state == "2binvoiced" for m in self.mapped("move_lines")):
            self.write({"invoice_state": "2binvoiced"})
        return super().action_assign()
