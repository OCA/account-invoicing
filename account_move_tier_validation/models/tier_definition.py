# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    open_mail_composer_wizard = fields.Boolean(
        "Open Mail Composer Wizard when Requesting Validation",
    )

    @api.model
    def _get_tier_validation_model_names(self):
        res = super(TierDefinition, self)._get_tier_validation_model_names()
        res.append("account.move")
        return res
