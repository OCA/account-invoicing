from odoo import _, fields, models
from odoo.exceptions import UserError


class Move(models.Model):
    _inherit = "account.move"

    proforma_number = fields.Char(string="Pro-forma Number", copy=False)
    proforma_date = fields.Date("Pro-forma Date", copy=False)

    def assign_proforma_number(self):
        for move in self:
            if not move.journal_id.pro_forma_sequence_id:
                raise UserError(
                    _("Journal %s does not have a pro-forma sequence")
                    % move.journal_id.display_name
                )
            date = move.date or fields.Date.today()
            move.proforma_number = move.journal_id.pro_forma_sequence_id.with_context(
                ir_sequence_date=date
            ).next_by_id()
            move.proforma_date = date

    def print_proforma(self):
        return self.env.ref(
            "account_invoice_pro_forma_sequence.account_invoices_proforma"
        ).report_action(self)
