# Copyright 2021 Julien Guenat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MassSendPrint(models.TransientModel):
    _name = "mass.send.print"
    _description = "Mass Send Print"

    template = fields.Many2one(
        comodel_name='mail.template',
        string='Use template',
        domain="[('model', '=', 'account.invoice')]",
    )

    def wizard_mass_send_print(self):
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)
        invoices.mass_send_print(self.template)
