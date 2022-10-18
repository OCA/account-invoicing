from odoo import models, api


class Move(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("force_move_type"):
            move_type = self.env.context["force_move_type"]
            self = self.with_context(default_move_type=move_type)
            for vals in vals_list:
                vals["move_type"] = move_type
        return super(Move, self).create(vals_list)
