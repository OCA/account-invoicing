# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.tools import UserError


class AccountProductMove(models.Model):
    _name = "account.product.move"
    _description = "Template for additional journal entries/items"

    @api.depends("journal_id")
    def _compute_company_id(self):
        """Company must correspond to journal."""
        for move in self:
            move.company_id = (
                move.journal_id.company_id or move.company_id or self.env.company
            )

    name = fields.Char(required=True, copy=False, default="New")
    state = fields.Selection(
        selection=[("new", "New"), ("complete", "Complete")],
        default="new",
        required=True,
    )
    journal_id = fields.Many2one(comodel_name="account.journal", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        store=True,
        readonly=True,
        compute="_compute_company_id",
    )
    line_ids = fields.One2many(
        comodel_name="account.product.move.line",
        inverse_name="move_id",
        copy=True,
        string="Extra Journal Items",
        help="Journal items to be added in new journal entry",
    )
    active = fields.Boolean(default=True)

    def button_complete(self):
        """Setting move to complete."""
        self.ensure_one()
        self._check_balanced()
        self.state = "complete"

    def button_reset(self):
        """Setting move to new."""
        self.ensure_one()
        self.state = "new"

    def action_toggle_active(self):
        self.ensure_one()
        self.active = not self.active

    def _check_balanced(self):
        """An adaptation of account.move._check_balanced()"""
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return
        self.env["account.product.move.line"].flush(
            self.env["account.product.move.line"]._fields
        )
        self._cr.execute(
            """
            SELECT
                line.move_id,
                ROUND(SUM(line.debit - line.credit),
                currency.decimal_places)
            FROM account_product_move_line line
            JOIN account_product_move move ON
                move.id = line.move_id
            JOIN res_company company ON
                company.id = move.company_id
            JOIN res_currency currency ON
                currency.id = company.currency_id
            WHERE
                line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        """,
            [tuple(self.ids)],
        )

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            raise UserError(
                _(
                    "Cannot create unbalanced journal entry. "
                    "Ids: %s\nDifferences debit - credit: %s"
                )
                % (ids, sums)
            )
