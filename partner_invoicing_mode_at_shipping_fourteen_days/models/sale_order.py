# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.osv.expression import AND


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_per_shipping_to_validate_invoices_domain(
        self, companies, invoicing_mode="standard"
    ) -> list:
        """
            This will return the domain for invoices that should be posted.
        :return: Domain
        :rtype: list
        """
        domain = super()._get_per_shipping_to_validate_invoices_domain(
            companies=companies, invoicing_mode=invoicing_mode
        )
        if invoicing_mode == "fourteen_days":
            domain = AND(
                [domain, [("partner_id.next_invoice_date", "<=", fields.Date.today())]]
            )
        return domain
