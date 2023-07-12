# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from ast import literal_eval

from odoo import _, api, models
from odoo.osv.expression import is_leaf


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

    @api.depends(lambda self: self._compute_need_validation_dependencies())
    def _compute_need_validation(self):
        for rec in self:
            tiers = self.env["tier.definition"].search([("model", "=", self._name)])
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = (
                not rec.review_ids and valid_tiers and rec._check_state_from_condition()
            )

    def _compute_need_validation_dependencies(self):
        """Return the fields the validation flag depends on"""
        if self._abstract:
            return []
        tiers = self.env["tier.definition"].search([("model", "=", self._name)])
        tier_domains = sum(
            (literal_eval(tier.definition_domain or "[]") for tier in tiers),
            [],
        )
        return list(
            leaf[0]
            for leaf in tier_domains
            if is_leaf(leaf) and leaf[0] in self._fields
        )
