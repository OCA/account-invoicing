# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# Copyright 2022 Simone Rubino - TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    sale_qty_to_reinvoice = fields.Boolean(
        string="This credit note will be reinvoiced",
        default=True,
        help="Leave it marked if you will reinvoice the same sale order line "
        "(standard behaviour)",
    )

    def invoice_refund(self):
        return super(
            AccountInvoiceRefund,
            self.with_context(sale_qty_to_reinvoice=self.sale_qty_to_reinvoice),
        ).invoice_refund()
