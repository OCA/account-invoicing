# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_is_transmit = fields.Boolean(
        string='Tranmit', related='company_id.invoice_is_transmit',
        readonly=False,
    )
    group_multi_transmit = fields.Boolean(
        string='Multiple Transmit Methods',
        implied_group='account_invoice_transmit_method.group_multi_transmit_method',
    )
