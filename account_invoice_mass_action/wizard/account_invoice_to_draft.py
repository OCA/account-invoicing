# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountInvoiceToDraft(models.TransientModel):
    """
    This wizard will set to draft all the selected open invoices
    """

    _name = "account.invoice.to.draft"
    _description = "Reset to Draft selected invoices if they are Opened"

    invoice_with_payment_ids = fields.One2many(
        comodel_name="account.invoice.to.draft.line",
        inverse_name="wiz_with_payment_id",
        string="With payment",
    )

    invoice_without_payment_ids = fields.One2many(
        comodel_name="account.invoice.to.draft.line",
        inverse_name="wiz_without_payment_id",
        string="Without payment",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if (
            "invoice_with_payment_ids" in fields_list
            and "invoice_without_payment_ids" in fields_list
        ):
            active_ids = self.env.context.get("active_ids", [])
            invoices = self.env["account.invoice"].browse(active_ids)
            res["invoice_with_payment_ids"] = []
            res["invoice_without_payment_ids"] = []
            for invoice in invoices:
                if invoice.payment_ids:
                    res["invoice_with_payment_ids"].append(
                        (
                            0,
                            0,
                            {
                                "invoice_id": invoice.id,
                                "number": invoice.number,
                                "partner_id": invoice.partner_id.id,
                                "date_invoice": invoice.date_invoice,
                                "amount_total": invoice.amount_total,
                                "residual": invoice.residual,
                                "currency_id": invoice.currency_id.id,
                            },
                        )
                    )
                else:
                    res["invoice_without_payment_ids"].append(
                        (
                            0,
                            0,
                            {
                                "invoice_id": invoice.id,
                                "number": invoice.number,
                                "partner_id": invoice.partner_id.id,
                                "date_invoice": invoice.date_invoice,
                                "amount_total": invoice.amount_total,
                                "residual": invoice.residual,
                                "currency_id": invoice.currency_id.id,
                            },
                        )
                    )
        return res

    @api.multi
    def invoices_to_draft(self):
        lines = (
            self.invoice_with_payment_ids | self.invoice_without_payment_ids
        )
        invoices = lines.mapped("invoice_id")

        invoices.action_invoice_cancel()
        invoices.action_invoice_draft()

        action_ref = self.env.ref("account.action_invoice_tree1")
        action_data = action_ref.read()[0]
        action_data["domain"] = [("id", "in", invoices.ids)]
        return action_data


class AccountInvoiceToDraftLine(models.TransientModel):
    """
    This wizard will set to draft all the selected open invoices
    """

    _name = "account.invoice.to.draft.line"
    _description = "Reset to Draft lines invoices if they are Opened"

    wiz_with_payment_id = fields.Many2one(
        comodel_name="account.invoice.to.draft",
        ondelete="cascade",
        string="Wizard with payment",
    )
    wiz_without_payment_id = fields.Many2one(
        comodel_name="account.invoice.to.draft",
        ondelete="cascade",
        string="Wizard without payment",
    )
    invoice_id = fields.Many2one(comodel_name="account.invoice")
    number = fields.Char(related="invoice_id.number")
    partner_id = fields.Many2one(related="invoice_id.partner_id")
    date_invoice = fields.Date(related="invoice_id.date_invoice")
    amount_total = fields.Monetary(related="invoice_id.amount_total")
    residual = fields.Monetary(related="invoice_id.residual")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
