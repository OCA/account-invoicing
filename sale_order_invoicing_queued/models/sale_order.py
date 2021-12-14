# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="order_id",
        column2="job_id",
        string="Invoicing Jobs",
        copy=False,
    )

    def create_invoices_job(self, final):
        self._create_invoices(final=final)
