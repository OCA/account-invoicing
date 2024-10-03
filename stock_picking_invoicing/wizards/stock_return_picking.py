# @ 2021-Today: Akretion - www.akretion.com -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    invoice_state = fields.Selection(
        selection=[("2binvoiced", "To be refunded/invoiced"), ("none", "No invoicing")],
        string="Invoicing",
        required=True,
        default="none",
    )

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super()._prepare_move_default_values(return_line, new_picking)
        if self.invoice_state == "2binvoiced":
            vals.update({"invoice_state": self.invoice_state})

        return vals
