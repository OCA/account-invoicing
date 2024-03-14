# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ShipmentAdvice(models.Model):
    _inherit = "shipment.advice"

    def print_cash_on_delivery_invoices(self):
        done_shipment_advices = self.filtered(lambda s: s.state == "done")
        cod_invoices = done_shipment_advices.mapped("loaded_picking_ids").mapped(
            "cash_on_delivery_invoice_ids"
        )
        if cod_invoices:
            return self.env.ref(
                "account.account_invoices_without_payment"
            ).report_action(cod_invoices)
        return {}
