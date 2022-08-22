# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        sale = self.env["sale.order"].search(
            [("name", "=", self.invoice_origin)], limit=1
        )
        for order in sale:
            if order.customer_need_po and not order.client_order_ref:
                raise ValidationError(
                    _(
                        "You can not confirm sale order without \
                                    Customer reference."
                    )
                )
            if order.sale_doc and not order.sale_document_option:
                raise ValidationError(
                    _(
                        "You can not confirm sale order without \
                                    Sale Documentation."
                    )
                )
        return super(AccountMove, self).action_post()
