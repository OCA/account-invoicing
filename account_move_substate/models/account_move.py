# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("account.move", "Account Move")],
        ondelete={"account.move": "cascade"},
    )


class AccountMove(models.Model):
    _inherit = ["account.move", "base.substate.mixin"]
    _name = "account.move"
    _state_field = "state"

    def _track_template(self, changes):
        res = super(AccountMove, self)._track_template(changes)
        track = self[0]
        if "substate_id" in changes and track.substate_id.mail_template_id:
            res["substate_id"] = (
                track.substate_id.mail_template_id,
                {
                    "composition_mode": "comment",
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res
