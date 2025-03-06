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


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    def _prepare_move_default_values(self, new_picking):
        vals = super()._prepare_move_default_values(new_picking)
        if self.wizard_id.invoice_state == "2binvoiced":
            vals.update({"invoice_state": self.wizard_id.invoice_state})
        return vals
