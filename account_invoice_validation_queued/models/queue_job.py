# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class QueueJob(models.Model):
    _inherit = 'queue.job'

    def cancel(self):
        self.filtered(lambda x: x.state in ['pending', 'enqueued']).unlink()
