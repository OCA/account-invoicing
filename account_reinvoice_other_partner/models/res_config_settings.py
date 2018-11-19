# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reinvoice_journal_id = fields.Many2one(
        'account.journal', string="Reinvoice Journal",
        related='company_id.reinvoice_journal_id')
