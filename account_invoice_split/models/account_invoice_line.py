from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    split = fields.Boolean(string="Split")
    state = fields.Selection(related="invoice_id.state")
