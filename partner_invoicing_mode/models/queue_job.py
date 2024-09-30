# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def related_action_open_invoice(self):
        """Open a form view with the invoice related to the job."""
        action = self.related_action_open_record()
        if len(self.records.exists()) > 1:
            action["view_id"] = self.env.ref("account.view_out_invoice_tree").id
        return action
