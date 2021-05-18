# Copyright 2021 - Elmonitor <info@elmonitor.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import config


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.onchange('partner_id')
    def onchange2_partner_id(self):
        if self.partner_id:
            self.user_id=self.partner_id.user_id.id or self.partner_id.commercial_partner_id.user_id.id or self.env.uid