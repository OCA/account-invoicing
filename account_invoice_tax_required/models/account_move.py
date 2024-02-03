# Copyright 2015 - Camptocamp SA - Author Vincent Renaville
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# Copyright 2019 - Punt Sistemes - Juan Vicente Pascual
# Copyright 2019-2024 - Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, models
from odoo.exceptions import RedirectWarning
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    def _test_invoice_line_tax(self):
        errors = []
        invoice_error_ids = []
        error_template = _(
            "Invoice %(invoice)s for customer %(customer)s "
            "has a line with product %(product)s with no taxes"
        )
        for invoice_line in self.mapped("invoice_line_ids").filtered(
            lambda x: x.display_type is False
        ):
            if not invoice_line.tax_ids:
                error_string = error_template % {
                    "invoice": invoice_line.move_id.name,
                    "customer": invoice_line.partner_id.name,
                    "product": invoice_line.name,
                }
                invoice_error_ids.append(invoice_line.move_id.id)
                errors.append(error_string)
        if errors:
            invoice_error_ids = list(set(invoice_error_ids))
            action_error = {
                "name": _("Invoices with Missing Taxes"),
                "res_model": "account.move",
                "type": "ir.actions.act_window",
                "search_view_id": [
                    self.env.ref("account.view_account_move_filter").id,
                    "search",
                ],
            }
            if len(invoice_error_ids) == 1:
                action_error["view_mode"] = "form"
                action_error["res_id"] = invoice_error_ids[0]
                action_error["views"] = [
                    [self.env.ref("account.view_move_form").id, "form"],
                ]
            else:
                action_error["view_mode"] = "tree"
                action_error["domain"] = [("id", "in", invoice_error_ids)]
                action_error["views"] = [
                    [self.env.ref("account.view_move_tree").id, "list"],
                    [self.env.ref("account.view_move_form").id, "form"],
                ]
            error_msg = "%(message)s\n%(errors)s" % {
                "message": _("No Taxes Defined!"),
                "errors": "\n".join(errors),
            }
            raise RedirectWarning(
                error_msg, action_error, _("Show invoices with lines without taxes")
            )

    def _post(self, soft=True):
        # Always test if it is required by context
        force_test = self.env.context.get("test_tax_required")
        skip_test = any(
            (
                # It usually fails when installing other addons with demo data
                self.with_user(SUPERUSER_ID)
                .env["ir.module.module"]
                .search(
                    [
                        ("state", "in", ["to install", "to upgrade"]),
                        ("demo", "=", True),
                    ]
                ),
                # Avoid breaking unaware addons' tests by default
                config["test_enable"],
            )
        )
        if force_test or not skip_test:
            self.filtered(lambda m: m.is_invoice())._test_invoice_line_tax()
        return super()._post(soft=soft)
