# Copyright <2020> PESOL <info@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from werkzeug.urls import url_encode

from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["posted"]

    user_validation_responsible_id = fields.Many2one(
        comodel_name="res.users", string="Validation Responsible"
    )

    def button_request_validation(self):
        for account_move in self:
            res = super().request_validation()
            tier_definitions = self.env["tier.definition"].search(
                [
                    ("model", "=", "account.move"),
                    ("open_mail_composer_wizard", "=", True),
                ]
            )
            for td in tier_definitions:
                if account_move.evaluate_tier(td):
                    action = self.env.ref(
                        "account_move_tier_validation.invoice_send_validation_request"
                    )
                    return action.read()[0]
            return res

    def get_web_url(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        url_params = url_encode(
            {
                "id": self.id,
                "view_type": "form",
                "model": "account.move",
                "action": self.env.ref("account.action_move_in_invoice_type").id,
            }
        )
        return f"{base_url}/web#{url_params}"
