from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_validate_invoice_negative_total_amount = fields.Boolean(
        """Allow validating an invoice with a negative total amount""",
        implied_group="account_invoice_negative_total.group_validate_invoice_negative_total_amount",  # noqa: E501
        help="""Allows you to validate an invoice with a negative total amount""", # noqa
    )
