# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection(
        selection_add=[("at_shipping", "At Shipping")],
        ondelete={"at_shipping": "set default"},
    )

    one_invoice_per_shipping = fields.Boolean(
        index=True,
        help="Check this if you want to create one invoice per shipping using the"
        " partner invoicing mode that should be different than 'At Shipping'.",
    )

    @api.constrains(
        "invoicing_mode", "one_invoice_per_shipping", "one_invoice_per_order"
    )
    def _check_invoicing_mode_one_invoice_per_shipping(self):
        for partner in self:
            if (
                partner.invoicing_mode == "at_shipping"
                and partner.one_invoice_per_shipping
            ):
                raise ValidationError(
                    _(
                        "You cannot configure the partner %(partner)s with "
                        "Invoicing Mode 'At Shipping' and 'One Invoice Per Shipping'!",
                        partner=partner.name,
                    ),
                )
            if partner.one_invoice_per_shipping and partner.one_invoice_per_order:
                raise ValidationError(
                    _(
                        "You cannot configure the partner %(partner)s with "
                        "'One Invoice Per Order' and 'One Invoice Per Shipping'!",
                        partner=partner.name,
                    ),
                )
