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
