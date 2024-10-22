# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.osv.expression import AND


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _create_extra_moves(self):
        move_model = self.env["account.move"]
        for line in self:
            # Concattenate product moves for categories and product templates.
            product_moves = (
                line.product_id.product_tmpl_id.product_move_ids
                | line.product_id.product_tmpl_id.categ_id.product_move_ids
            )
            if not product_moves:
                continue
            for product_move in product_moves:
                if not line._is_product_move_valid(product_move):
                    continue
                vals = line._prepare_move_vals(product_move)
                extra_move = move_model.create(vals)
                line._create_extra_move_lines(product_move, extra_move)
                extra_move.action_post()

    def _prepare_move_vals(self, product_move):
        """Values for creation of extra product move."""
        self.ensure_one()
        return {
            "type": "entry",
            "ref": self.move_id.name,
            "journal_id": product_move.journal_id.id,
            "partner_id": self.move_id.partner_id.id,
            "date": self.move_id.invoice_date,
            "invoice_move_id": self.move_id.id,
            "invoice_origin": self.move_id.name,
        }

    def _is_product_move_valid(self, product_move):
        """Check wether product.move valid for this move and line."""
        self.ensure_one()
        if product_move.state != "complete":
            return False
        if not product_move.filter_id:
            return True
        # Sanity check domain.
        zfilter = product_move.filter_id  # filter without z is a builtin.
        if zfilter.user_id or zfilter.domain == "[]":
            return True
        # Check wether main move would be selected by filter.
        filter_domain = zfilter._get_eval_domain()
        check_domain = AND([[("id", "=", self.move_id.id)], filter_domain])
        move_model = self.env["account.move"]
        if move_model.search(check_domain, limit=1):
            # record would be selected.
            return True
        return False

    def _create_extra_move_lines(self, product_move, extra_move):
        """Create extra move lines for product move."""
        self.ensure_one()
        for product_move_line in product_move.line_ids:
            vals = self._prepare_move_line_vals(product_move_line, extra_move)
            extra_move_line = self.with_context(check_move_validity=False).create(vals)
            extra_move_line._onchange_currency()

    def _prepare_move_line_vals(self, product_move_line, extra_move):
        """Prepare vals for extra move line."""
        self.ensure_one()
        line_vals = {
            "move_id": extra_move.id,
            "partner_id": self.move_id.partner_id.id,
        }
        return product_move_line._complete_line_vals(self, line_vals)
