# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.tools import UserError


class AccountMoveJournalTemplate(models.Model):
    _name = "account.move.journal.template"
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
        comodel_name="account.move.journal.template.item.line",
        inverse_name="journal_template_id",
        copy=True,
        string="Journal Items",
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
        self.env["account.move.journal.template.item.line"].flush(
            self.env["account.move.journal.template.item.line"]._fields
        )
        self._cr.execute(
            """
            SELECT
                line.journal_template_id,
                ROUND(SUM(line.debit - line.credit),
                currency.decimal_places)
            FROM account_move_journal_template_item_line line
            JOIN account_move_journal_template move ON
                move.id = line.journal_template_id
            JOIN res_currency currency ON
                currency.id = company.currency_id
            WHERE
                line.journal_template_id IN %s
            GROUP BY line.journal_template_id, currency.decimal_places
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
        res = super().write(vals)
        for this in self:
            # this._check_balanced()
            this.product_tmpl_id.journal_tmpl_id = this
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # records._check_balanced()
        for this in records:
            this.product_tmpl_id.journal_tmpl_id = this
        return records


class ProductTemplate(models.Model):
    _inherit = "product.template"

    journal_tmpl_id = fields.Many2one(
        comodel_name="account.move.journal.template", string="Journal Template",
    )


class AccountMoveJournalTemplateItemLine(models.Model):
    _name = "account.move.journal.template.item.line"
    _description = "Items for journal entry for given products"

    debit = fields.Monetary(default=0.0)
    credit = fields.Monetary(default=0.0)
    account_id = fields.Many2one(
        comodel_name="account.account", ondelete="cascade", required=True
    )
    currency_id = fields.Many2one("res.currency")
    journal_template_id = fields.Many2one(comodel_name="account.move.journal.template")
