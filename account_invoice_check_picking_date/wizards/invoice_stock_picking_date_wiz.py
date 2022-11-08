# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class InvoicePickingDateCheckWiz(models.TransientModel):
    _name = "invoice.picking.date.check.wiz"
    _description = "Invoice and picking date check wizard"

    invoice_id = fields.Many2one(comodel_name="account.move")
    exception_msg = fields.Text(readonly=True)

    def action_show(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice date does not match with stock move dates"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def button_continue(self):
        self.ensure_one()
        return self.invoice_id.with_context(
            skip_account_invoice_check_picking_date=True
        ).action_post()
