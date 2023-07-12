# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("account.move")
        return res

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._update_registry()
        return result

    def write(self, vals):
        result = super().write(vals)
        if "definition_domain" in vals:
            self._update_registry()
        return result

    def unlink(self):
        models = set(self.mapped("model"))
        result = super().unlink()
        self._update_registry(models)
        return result

    def _update_registry(self, models=None):
        """Update dependencies of validation flag"""
        for model in models or set(self.mapped("model")):
            depends = self.env[model]._compute_need_validation._depends
            if not callable(depends):
                continue
            self.pool.field_depends[
                self.env[model]._fields["need_validation"]
            ] = depends(self.env[model])
            self.pool.registry_invalidated = True
