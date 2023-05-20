# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        """
        Inherit to update related picking as '2binvoiced' when the invoice is
        cancelled (only for invoices, not refunds)
        :return: bool
        """
        result = super().button_cancel()
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
        pickings._set_as_2binvoiced()
        return result

    def button_draft(self):
        result = super().button_draft()
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_invoiced()
        pickings._set_as_invoiced()
        return result

    def unlink(self):
        """
        Inherit the unlink to update related picking as "2binvoiced"
        (only for invoices, not refunds)
        :return:
        """
        pickings = self.filtered(
            lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
        ).mapped("picking_ids")
        self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
        pickings._set_as_2binvoiced()
        return super().unlink()
