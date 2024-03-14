# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    cash_on_delivery = fields.Boolean("Cash on Delivery")
    auto_validate_invoice = fields.Boolean()
