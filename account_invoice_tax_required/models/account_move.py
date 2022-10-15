# Copyright 2015 - Camptocamp SA - Author Vincent Renaville
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# Copyright 2019 - Tecnativa - Pedro M. Baeza
# Copyright 2019 - Punt Sistemes - Juan Vicente Pascual
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, models
from odoo.exceptions import UserError
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    def _test_invoice_line_tax(self):
        errors = []
        error_template = _("Invoice has a line with product %s with no taxes")
        for invoice_line in self.mapped("invoice_line_ids").filtered(
            lambda x: x.display_type not in ("line_section", "line_note")
        ):
            if not invoice_line.tax_ids:
                error_string = error_template % (invoice_line.name)
                errors.append(error_string)
        if errors:
            raise UserError(
                _(
                    "%(message)s\n%(errors)s",
                    message="No Taxes Defined!",
                    errors=("\n".join(x for x in errors)),
                )
            )

    def action_post(self):
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
        for move in self:
            if move.move_type != "entry" and (force_test or not skip_test):
                move._test_invoice_line_tax()
        return super(AccountMove, self).action_post()
