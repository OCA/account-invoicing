from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def open_invoice_date_wizard(self):

        if self.invoice_date or not self.move_type.endswith("_invoice"):
            self.action_post()
        else:
            name = _("Confirm %s") % self.type_name
            action = self.env.ref(
                "account_invoice_date.view_account_voucher_proforma_date"
            )
            return {
                "name": name,
                "view_type": "form",
                "target": "new",
                "res_model": "account.voucher.proforma.date",
                "views": [(action.id, "form")],
                "type": "ir.actions.act_window",
            }
