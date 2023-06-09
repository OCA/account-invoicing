# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_open_invoice_clearing_wizard(self):
        wizard = (
            self.env["account.invoice.clearing.wizard"]
            .with_context(active_model=self._name, active_ids=self.ids)
            .create({"invoice_ids": [(6, 0, self.ids)]})
        )
        wizard._compute_initial_data()
        wizard._onchange_move_type()
        action = (
            self.sudo()
            .env.ref("account_invoice_clearing.action_account_invoice_clearing_wizard")
            .read()[0]
        )
        action["res_id"] = wizard.id
        return action
