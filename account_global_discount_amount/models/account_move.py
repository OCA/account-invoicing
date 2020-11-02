# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = ["account.move", "discount.mixin"]
    _name = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        # When duplicate invoice, debits and credits must be balanced
        if self.env.context.get("not_discount_lines_from_copy", False):
            for vals in vals_list:
                if vals["global_discount_amount"] != 0.0:
                    debit_lines = [
                        line
                        for line in vals["line_ids"]
                        if not line[2].get("is_discount_line", False)
                        and line[2].get("debit", 0.0) != 0.0
                    ]
                    debit_lines[0][2].update({"debit": self.amount_total})
        moves = super().create(vals_list)
        for i, vals in enumerate(vals_list):
            if (
                vals
                and "global_discount_amount" in vals
                and vals["global_discount_amount"] != 0.0
                and moves[i].amount_untaxed != 0.0
                and not self.env.context.get("discount_lines_from_sale", False)
                and not self.env.context.get("not_discount_lines_from_copy", False)
            ):
                self.env["account.move.line"]._create_discount_lines(move=moves[i])
                moves[i].with_context(check_move_validity=False)._recompute_tax_lines()
        return moves

    def write(self, vals):
        res = super().write(vals)
        for move in self:
            if (
                (
                    "global_discount_amount" in vals
                    or "line_ids" in vals
                    or not move.global_discount_ok
                )
                and not self.env.context.get("discount_lines", False)
                and not self.env.context.get("discount_lines_from_sale", False)
            ):
                # we can not unlink move lines linked with sale lines
                move.invoice_line_ids.filtered(
                    lambda x: x.is_discount_line
                ).with_context(check_move_validity=False, discount_lines=True).unlink()
                move.line_ids.filtered(lambda x: x.is_discount_line).with_context(
                    check_move_validity=False, discount_lines=True
                ).unlink()
                move.with_context(
                    check_move_validity=False, discount_lines=True
                )._recompute_tax_lines()
                if move.global_discount_amount != 0.0:
                    self.env["account.move.line"]._create_discount_lines(move=move)
                    move.with_context(
                        check_move_validity=False, discount_lines=True
                    )._recompute_tax_lines()
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        # for not create the discount lines
        self = self.with_context(not_discount_lines_from_copy=True)
        return super().copy(default=default)


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "discount.line.mixin"]
    _name = "account.move.line"

    def _create_discount_lines(self, move):
        amount_untaxed = move.amount_untaxed
        # create discount lines by tax line
        with_tax_lines = move.line_ids.filtered(lambda x: x.tax_line_id)
        for line in with_tax_lines:
            tax_ids = [(6, 0, [line.tax_line_id.id])]
            tax_base_amount = line.tax_base_amount
            self._create_one_discount_line(
                move=move,
                tax_ids=tax_ids,
                tax_base_amount=tax_base_amount,
                amount_untaxed=amount_untaxed,
            )
        # create one discount line for the all invoice lines without tax lines
        lines_with_tax = move.line_ids.filtered(lambda x: x.tax_ids)
        line_tax_ids = lines_with_tax.tax_ids - with_tax_lines.tax_line_id
        without_tax_lines = move.invoice_line_ids.filtered(
            lambda x: x.tax_ids == line_tax_ids
        )
        without_tax_base_amount = 0.0
        for line in without_tax_lines:
            without_tax_base_amount += line.price_subtotal
        if without_tax_lines:
            tax_ids = [(6, 0, without_tax_lines.tax_ids.ids)]
            self._create_one_discount_line(
                move=move,
                tax_ids=tax_ids,
                tax_base_amount=without_tax_base_amount,
                amount_untaxed=amount_untaxed,
            )

    def _create_one_discount_line(self, move, tax_ids, tax_base_amount, amount_untaxed):
        global_discount_amount = move.global_discount_amount
        discount_product = self.env.ref(
            "account_global_discount_amount.discount_product"
        )
        discount_line = self.with_context(check_move_validity=False).create(
            {
                "product_id": discount_product.id,
                "move_id": move.id,
                "partner_id": move.partner_id.id,
                "quantity": 1,
                "account_id": move.line_ids[0]._get_computed_account().id,
            }
        )
        discount_line._onchange_product_id()
        price_unit = discount_line._prepare_discount_line_vals(
            amount_untaxed=amount_untaxed,
            tax_base_amount=tax_base_amount,
            global_discount_amount=global_discount_amount,
        )
        discount_line.write(
            {
                "price_unit": -1 * price_unit,
                "is_discount_line": True,
                "tax_ids": tax_ids,
            }
        )
