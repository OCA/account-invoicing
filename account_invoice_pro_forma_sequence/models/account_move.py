from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class Move(models.Model):
    _inherit = "account.move"

    proforma_number = fields.Char(string="Pro-forma Number", required=False, copy=False)
    proforma_date = fields.Date("Pro-forma Date", copy=False)

    def assign_proforma_number(self):
        if not self.journal_id.pro_forma_sequence_id:
            raise UserError(
                _("Journal %s does not have a pro-forma sequence")
                % self.journal_id.display_name
            )
        date = self.date or datetime.now().date()
        self.proforma_number = self.journal_id.pro_forma_sequence_id.with_context(
            ir_sequence_date=date
        ).next_by_id()
        self.proforma_date = date
