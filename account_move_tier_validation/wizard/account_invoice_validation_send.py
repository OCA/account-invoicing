# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import first


class AccountInvoiceSendValidation(models.TransientModel):
    _name = "account.invoice.send.validation"
    _inherits = {"mail.compose.message": "composer_id"}
    _description = "Account Invoice Send Validation Request"

    invoice_id = fields.Many2one("account.move", string="Invoice")
    composer_id = fields.Many2one(
        "mail.compose.message",
        string="Composer",
        required=True,
        ondelete="cascade",
    )
    template_id = fields.Many2one(
        "mail.template", index=True, domain="[('model', '=', 'account.move')]"
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res_ids = self._context.get("active_ids")
        invoice = first(self.env["account.move"].browse(res_ids))
        if not invoice:
            raise UserError(_("Invoice to request validation for has not been found"))
        composer = self.env["mail.compose.message"].create({})
        values = {
            "composition_mode": "mass_mail",
            "invoice_id": invoice.id,
            "composer_id": composer.id,
        }
        if invoice.user_validation_responsible_id:
            values["partner_ids"] = [
                (4, invoice.user_validation_responsible_id.partner_id.id, 0)
            ]
        if hasattr(invoice, "attachment_ids") and invoice.attachment_ids:
            values["attachment_ids"] = invoice.attachment_ids.ids
        res.update(values)
        return res

    @api.onchange("template_id")
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                wizard.composer_id.onchange_template_id_wrapper()

    def send_action(self):
        self.ensure_one()
        if not self.partner_ids:
            raise ValidationError(_("An email recipient is required."))
        self.composer_id.send_mail()
        return {"type": "ir.actions.act_window_close"}
