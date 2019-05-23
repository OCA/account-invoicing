# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EbillPaymentContract(models.Model):

    _name = "ebill.payment.contract"
    _description = "Ebill Payment Contract"
    _rec_name = "name"

    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method",
        string="Transmit method",
        ondelete="restrict",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    name = fields.Char(related="partner_id.name")
    date_start = fields.Date(
        string="Start date",
        required=True,
        default=lambda self: fields.Date.today(),
    )
    date_end = fields.Date(string="End date")
    state = fields.Selection(
        selection=[("draft", "Draft"), ("open", "Open"), ("cancel", "Cancel")],
        required=True,
        default='draft',
    )
    is_valid = fields.Boolean(compute="_compute_is_valid")

    @api.onchange('state')
    def _compute_state_changed(self):
        """Change the end date if contract is canceled."""
        if self.state == 'cancel' and self.date_end > fields.Date.today():
            self.date_end = fields.Date.today()

    @api.multi
    @api.depends("state", "date_start", "date_end")
    def _compute_is_valid(self):
        """ Check that the contract is valid

        It is valid if the contract is opened and his start date is in the pass
        And his end date is in the future or not set.
        """
        for contract in self:
            contract.is_valid = (
                contract.state == "open"
                and contract.date_start
                and contract.date_start <= fields.Date.today()
                and (
                    not contract.date_end
                    or contract.date_end >= fields.Date.today()
                )
            )
