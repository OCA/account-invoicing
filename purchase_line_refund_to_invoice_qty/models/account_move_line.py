# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_qty_to_reinvoice = fields.Boolean(
        string="Purchase qty to reinvoice",
        help="Leave it marked if you will reinvoice the same purchase order line",
    )
