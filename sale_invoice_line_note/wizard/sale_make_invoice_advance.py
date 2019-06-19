# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    copy_notes_to_invoice = fields.Boolean(
        default=True,
        string="Copy notes to invoice",
        help="Mark this to create invoice line notes from the notes in the "
             "sale order",
    )

    @api.multi
    def create_invoices(self):
        if self.copy_notes_to_invoice:
            self = self.with_context(_copy_notes=True)
        return super().create_invoices()
