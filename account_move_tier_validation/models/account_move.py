# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["posted"]

    _tier_validation_manual_config = False

    @api.depends("need_validation")
    def _compute_hide_post_button(self):
        result = super()._compute_hide_post_button()
        for this in self:
            this.hide_post_button |= this.need_validation
        return result

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + ["needed_terms_dirty"]

    def _get_to_validate_message_name(self):
        name = super()._get_to_validate_message_name()
        if self.move_type == "in_invoice":
            name = _("Bill")
        elif self.move_type == "in_refund":
            name = _("Refund")
        elif self.move_type == "out_invoice":
            name = _("Invoice")
        elif self.move_type == "out_refund":
            name = _("Credit Note")
        return name

    def action_post(self):
        return super(
            AccountMove, self.with_context(skip_validation_check=True)
        ).action_post()
