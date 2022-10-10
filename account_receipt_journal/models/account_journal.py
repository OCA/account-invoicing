from odoo import fields, models


class Journal(models.Model):
    _inherit = "account.journal"
    receipts = fields.Boolean(string="Receipts")
