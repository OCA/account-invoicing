# Copyright 2016 Chafique DELLI @ Akretion
# Copyright 2016-Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Column Section
    supplier_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier Partner",
        compute="_compute_supplier_partner_id",
    )

    supplierinfo_ok = fields.Boolean(
        string="Supplier Informations Checked",
        copy=False,
        help="Checked if the check of supplierinfo has been done.\n"
        " - Uncheck this box, if you want to check again this invoice\n"
        " - Check this box, if you want to mark this invoice as checked",
    )

    # Compute Section
    def _compute_supplier_partner_id(self):
        for invoice in self:
            invoice.supplier_partner_id = (
                invoice.partner_id.commercial_partner_id or invoice.partner_id
            )

    # Custom Section
    def _get_update_supplierinfo_lines(self):
        self.ensure_one()
        lines = []
        product_ids = []

        for line in self.invoice_line_ids.filtered(lambda x: x.product_id):
            # We the invoice has two or more lines with the same product,
            # the computation will be based only on the first line.
            if line.product_id.id in product_ids:
                continue
            else:
                product_ids.append(line.product_id.id)

            # Get supplierinfo if exist
            supplierinfo = line._get_supplierinfo()

            # Test if supplierinfo price  matches with line info
            if supplierinfo:
                if line._is_correct_price(supplierinfo):
                    continue

            # Propose updating, if needed
            lines.append((0, 0, line._prepare_supplier_wizard_line(supplierinfo)))
        return lines

    # View Section
    def check_supplierinfo(self):
        self.ensure_one()
        lines_for_update = self._get_update_supplierinfo_lines()
        if lines_for_update:
            ctx = {
                "default_line_ids": lines_for_update,
                "default_invoice_id": self.id,
            }

            view_form = self.env.ref(
                "account_invoice_supplierinfo_update."
                "view_wizard_update_invoice_supplierinfo_form"
            )
            return {
                "name": _("Update supplier informations of products"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "wizard.update.invoice.supplierinfo",
                "views": [(view_form.id, "form")],
                "view_id": view_form.id,
                "target": "new",
                "context": ctx,
            }
        else:
            self.write({"supplierinfo_ok": True})
