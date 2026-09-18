# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    post_block_id = fields.Many2one(
        comodel_name="account.post.block.reason",
        string="Post Block Reason",
    )
    post_blocked = fields.Boolean(
        compute="_compute_post_blocked",
    )

    @api.depends("post_block_id")
    def _compute_post_blocked(self):
        for rec in self:
            rec.post_blocked = rec.post_block_id

    @api.model
    def create(self, vals):
        am = super().create(vals)
        if "post_block_id" in vals and vals["post_block_id"]:
            am.message_post(
                body=_('Entry "%(move_name)s" blocked with reason' "%(reason)s")
                % {"move_name": am.name, "reason": am.post_block_id.name}
            )
        return am

    def write(self, vals):
        res = super().write(vals)
        for am in self:
            if "post_block_id" in vals and vals["post_block_id"]:
                am.message_post(
                    body=_("Entry %(move_name)s blocked with reason %(reason)s")
                    % {"move_name": am.name, "reason": am.post_block_id.name}
                )
            elif "post_block_id" in vals and not vals["post_block_id"]:
                am.message_post(body=_('Entry "%s" post block released.') % am.name)
        return res

    def button_release_post_block(self):
        for move in self:
            move.post_block_id = False
        return True
