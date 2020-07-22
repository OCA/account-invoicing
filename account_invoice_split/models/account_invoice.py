from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    split_id = fields.Many2one(
        string="Split From",
        comodel_name="account.invoice",
        help="INV Split From Ref:",
    )

    @api.multi
    def split_quotation(self):
        self.ensure_one()
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

        return new_invoice

    @api.multi
    def build_split_invoice_tree_view(self, split_invoice):
        compose_tree = compose_form = False
        if self.type == "in_invoice":
            compose_tree = self.env.ref("account.invoice_supplier_tree", False)
            compose_form = self.env.ref("account.invoice_supplier_form", False)
        elif self.type == "out_invoice":
            compose_tree = self.env.ref("account.invoice_tree", False)
            compose_form = self.env.ref("account.invoice_form", False)
        return {
            "name": "Split Records",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.invoice",
            "views": [(compose_tree.id, "tree"), (compose_form.id, "form")],
            "view_id": compose_tree.id,
            "res.id": False,
            "target": "current",
            "domain": [("id", "in", [self.id, split_invoice.id])],
            "context": {},
        }

    @api.multi
    def btn_split_quotation(self):
        self.ensure_one()
        lines_to_split = [line for line in self.invoice_line_ids if line.split]
        if lines_to_split:
            new_invoice = self.split_quotation()
            return self.build_split_invoice_tree_view(new_invoice)
        else:
            raise ValidationError(_("Please Select Line/Lines To Split"))
