from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def open_invoice_date_wizard(self):
        if self.invoice_date:
            self.action_post()
        else:
            if self.move_type == "out_invoice":
                name = _("Confirm Invoice")
            elif self.move_type == "in_invoice":
                name = _("Confirm Bill")
            elif self.move_type == "in_refund" or self.move_type == "out_refund":
                name = _("Confirm Credit Note")
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
