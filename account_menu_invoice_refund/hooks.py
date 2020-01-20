# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.account.models.account_payment import account_payment, payment_register

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    "out_invoice": "customer",
    "out_refund": "customer",
    "out_receipt": "customer",
    "in_invoice": "supplier",
    "in_refund": "supplier",
    "in_receipt": "supplier",
}


def post_load_hook():
    @api.model
    def new_default_get_payment_register(self, fields):
        """ Removed condition that disallow mixing invoice and refund """
        rec = super(payment_register, self).default_get(fields)
        active_ids = self._context.get("active_ids")
        invoices = self.env["account.move"].browse(active_ids)

        # Check all invoices are open
        if any(
            invoice.state != "posted"
            or invoice.invoice_payment_state != "not_paid"
            or not invoice.is_invoice()
            for invoice in invoices
        ):
            raise UserError(_("You can only register payments for open invoices"))
        if any(inv.company_id != invoices[0].company_id for inv in invoices):
            raise UserError(
                _(
                    """You can only register at the same time for payment that
                     are all from the same company"""
                )
            )
        if "invoice_ids" not in rec:
            rec["invoice_ids"] = [(6, 0, invoices.ids)]
        if "journal_id" not in rec:
            rec["journal_id"] = (
                self.env["account.journal"]
                .search(
                    [
                        ("company_id", "=", self.env.company.id),
                        ("type", "in", ("bank", "cash")),
                    ],
                    limit=1,
                )
                .id
            )
        if "payment_method_id" not in rec:
            if invoices[0].is_inbound():
                domain = [("payment_type", "=", "inbound")]
            else:
                domain = [("payment_type", "=", "outbound")]
            rec["payment_method_id"] = (
                self.env["account.payment.method"].search(domain, limit=1).id
            )
        return rec

    if not hasattr(payment_register, "default_get_original"):
        payment_register.default_get_original = payment_register.default_get

    payment_register.default_get = new_default_get_payment_register

    @api.model
    def new_default_get_account_payment(self, default_fields):
        """ Removed condition that disallow register
        payment between Invoice and Refund"""
        rec = super(account_payment, self).default_get(default_fields)
        active_ids = self._context.get("active_ids") or self._context.get("active_id")
        active_model = self._context.get("active_model")

        # Check for selected invoices ids
        if not active_ids or active_model != "account.move":
            return rec

        invoices = (
            self.env["account.move"]
            .browse(active_ids)
            .filtered(lambda move: move.is_invoice(include_receipts=True))
        )

        # Check all invoices are open
        if not invoices or any(invoice.state != "posted" for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))

        amount = self._compute_payment_amount(
            invoices,
            invoices[0].currency_id,
            invoices[0].journal_id,
            rec.get("payment_date") or fields.Date.today(),
        )

        rec.update(
            {
                "currency_id": invoices[0].currency_id.id,
                "amount": abs(amount),
                "payment_type": "inbound" if amount > 0 else "outbound",
                "partner_id": invoices[0].commercial_partner_id.id,
                "partner_type": MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
                "communication": invoices[0].ref or invoices[0].name,
                "invoice_ids": [(6, 0, invoices.ids)],
            }
        )
        return rec

    if not hasattr(account_payment, "default_get_original"):
        account_payment.default_get_original = account_payment.default_get

    account_payment.default_get = new_default_get_account_payment
