# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    cash_on_delivery = fields.Boolean(
        help="Check this if you want to identify Cash On Delivery invoices on stock pickings."
    )
    auto_validate_invoice_cash_on_delivery = fields.Boolean(
        help="Check this if you want Cash on Delivery deliveries to validate "
        "automatically generated invoices."
    )
