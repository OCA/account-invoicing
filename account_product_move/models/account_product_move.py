# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.tools import UserError


class AccountProductMove(models.Model):
    _name = "account.product.move"
    _description = "Template for additional journal entries/items"

    _sql_constraints = [
        (
            "product_tmpl_id",
            "UNIQUE (product_tmpl_id)",
            _("Template for this product already exists"),
        ),
    ]

    name = fields.Char(required=True, copy=False, default="New")
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        help="Journal items will be created for this product",
    )
    journal_item_ids = fields.One2many(
        comodel_name="account.product.move.line",
        inverse_name="product_move_id",
        copy=True,
        string="Extra Journal Items",
        help="Journal items to be added in new journal entry",
    )
    active = fields.Boolean(default=True)

    def action_toggle_active(self):
        self.ensure_one()
        self.active = not self.active

    def _check_balanced(self):
        """ An adaptation of account.move._check_balanced()"""
        moves = self.filtered(lambda move: move.journal_item_ids)
        if not moves:
            return
        self.env["account.product.move.line"].flush(
            self.env["account.product.move.line"]._fields
        )
        self._cr.execute(
            """
            SELECT
                line.product_move_id,
                ROUND(SUM(line.debit - line.credit),
                currency.decimal_places)
            FROM account_product_move_line line
            JOIN account_product_move move ON
                move.id = line.product_move_id
            JOIN account_journal journal ON
                journal.id = line.journal_id
            JOIN res_company company ON
                company.id = journal.company_id
            JOIN res_currency currency ON
                currency.id = company.currency_id
            WHERE
                line.product_move_id IN %s
            GROUP BY line.product_move_id, currency.decimal_places
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

    def write(self, vals):
        if "product_tmpl_id" in vals:
            for this in self:
                if not this.product_tmpl_id:
                    continue
                this.product_tmpl_id.journal_tmpl_id = False
        res = super().write(vals)
        for this in self:
            this._check_balanced()
            this.product_tmpl_id.journal_tmpl_id = this
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_balanced()
        for this in records:
            this.product_tmpl_id.journal_tmpl_id = this
        return records
