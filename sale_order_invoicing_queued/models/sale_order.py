# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

try:  # The try can be removed in v12 as not needed
    from odoo.addons.queue_job.job import job
except ImportError:
    import logging
    import functools

    logging.getLogger(__name__).debug("Can't `import queue_job`.")

    def job(*argv, **kwargs):
        return functools.partial


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_job_ids = fields.Many2many(
        comodel_name='queue.job',
        column1='order_id',
        column2='job_id',
        string="Invoicing Jobs",
        copy=False,
    )

    @job(default_channel='root.sale_order_invoicing_queued')
    def create_invoices_job(self, final):
        self.action_invoice_create(final=final)
