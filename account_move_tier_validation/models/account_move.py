# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["posted"]

    def _get_to_validate_message_name(self):
        name = super(AccountMove, self)._get_to_validate_message_name()
        if self.move_type == "in_invoice":
            name = _("Bill")
        elif self.move_type == "in_refund":
            name = _("Refund")
        elif self.move_type == "out_invoice":
            name = _("Invoice")
        elif self.move_type == "out_refund":
            name = _("Credit Note")
        return name
