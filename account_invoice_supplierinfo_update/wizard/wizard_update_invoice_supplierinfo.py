# Copyright 2016 Chafique DELLI @ Akretion
# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _name = "wizard.update.invoice.supplierinfo"
    _description = "Wizard to update supplierinfo"

    line_ids = fields.One2many(
        comodel_name="wizard.update.invoice.supplierinfo.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        required=True,
        readonly=True,
        ondelete="cascade",
    )

    state = fields.Selection(related="invoice_id.state", readonly=True)

    supplier_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        related="invoice_id.supplier_partner_id",
        readonly=True,
    )

    def update_supplierinfo(self):
        self.ensure_one()
        supplierinfo_obj = self.env["product.supplierinfo"]
        for line in self.line_ids:
            supplierinfo = line.supplierinfo_id
            # Create supplierinfo if not exist
            if not supplierinfo:
                supplierinfo_obj.create(line._prepare_supplierinfo())
            else:
                supplierinfo.write(line._prepare_supplierinfo_update())

        # Mark the invoice as checked
        self.invoice_id.write({"supplierinfo_ok": True})

    def set_supplierinfo_ok(self):
        self.invoice_id.write({"supplierinfo_ok": True})

    def update_supplierinfo_validate(self):
        self.update_supplierinfo()
        invoice = self.env["account.move"].browse(self._context["active_id"])
        invoice.post()
