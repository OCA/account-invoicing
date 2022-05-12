from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != "open")
        if self.user_has_groups(
            "account_invoice_negative_total."
            "group_validate_invoice_negative_total_amount"
        ) and to_open_invoices.filtered(
            lambda inv: float_compare(
                inv.amount_total,
                0.0,
                precision_rounding=inv.currency_id.rounding,
            )
            == -1
        ):
            return self.action_invoice_negative_amount_open(to_open_invoices)
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_invoice_negative_amount_open(self, to_open_invoices):
        """Similar to action_invoice_open without UserError on an invoice
        with a negative total amount"""
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(
                _(
                    "The field Vendor is required, please complete it to "
                    "validate the Vendor Bill. "
                )
            )
        if to_open_invoices.filtered(lambda inv: inv.state != "draft"):
            raise UserError(
                _("Invoice must be in draft state in order to validate it.")
            )
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _(
                    "No account was found to create the invoice, be sure you "
                    "have installed a chart of account. "
                )
            )
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()
