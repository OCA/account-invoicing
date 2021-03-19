# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveSetDueDate(models.TransientModel):
    _name = "account.move.set.due.date"
    _description = "Wizard to set due date"

    date_due = fields.Date(
        string="New Due Date",
        required=True,
        help="New date to be set to the invoice's due date.",
    )

    def action_set_due_date(self):
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")
        if not active_ids or active_model != "account.move":
            return False

        # Set due date on invoices
        invoices = self.env["account.move"].browse(active_ids)
        invoices.write({"invoice_date_due": self.date_due})

        # Set due date on account move lines
        amls = invoices.mapped("invoice_line_ids")
        amls.write({"date_maturity": self.date_due})
        return True
