from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceInherit(models.Model):
    _inherit = "account.invoice"

    split_id = fields.Many2one(
        string="Split From",
        comodel_name="account.invoice",
        help="INV Split From Ref:",
    )

    def btn_split_quotation(self):
        """
        Define function to split invoice when we click on button
        :return: New INV view
        """
        self.ensure_one()

        # split invoice
        lines_to_split = [line for line in self.invoice_line_ids if line.split]
        if lines_to_split:
            new_invoice = self.copy()
            new_invoice.split_id = self.id
            new_invoice.date_due = self.date_due
            for line in new_invoice.invoice_line_ids:
                if not line.split:
                    line.unlink()
                else:
                    line.split = False
            for line in self.invoice_line_ids:
                if line.split:
                    line.unlink()

            # build view
            compose_tree = compose_form = False
            if self.type == "in_invoice":
                compose_tree = self.env.ref(
                    "account.invoice_supplier_tree", False
                )
                compose_form = self.env.ref(
                    "account.invoice_supplier_form", False
                )
            elif self.type == "out_invoice":
                compose_tree = self.env.ref("account.invoice_tree", False)
                compose_form = self.env.ref("account.invoice_form", False)
            return {
                "name": "Split Records",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "account.invoice",
                "views": [
                    (compose_tree.id, "tree"),
                    (compose_form.id, "form"),
                ],
                "view_id": compose_tree.id,
                "res.id": False,
                "target": "current",
                "domain": [("id", "in", [self.id, new_invoice.id])],
                "context": {},
            }

        else:
            raise ValidationError(_("Please Select Line/Lines To Split"))
