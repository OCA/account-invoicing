from odoo import fields, models

HELP = "This account is used if the account in the current company is not defined"


class ProductCategory(models.Model):
    _inherit = "product.category"

    account_expense_parent_id = fields.Many2one(
        comodel_name="account.account",
        string="Parent Company Account Expense",
        compute="_compute_account_categ_parent",
        help=HELP,
    )
    account_income_parent_id = fields.Many2one(
        comodel_name="account.account",
        string="Parent Company Account Income",
        compute="_compute_account_categ_parent",
        help=HELP,
    )

    def _compute_account_categ_parent(self):
        company = self.env.company.parent_id or self.env.company

        def my_parent_account(product, myfield):
            return product.with_company(company.id)._get_category_account(myfield)

        for rec in self:
            product = self.env["product.template"].search(
                [("categ_id", "=", rec.id)], limit=1
            )
            rec.account_expense_parent_id = my_parent_account(
                product, "property_account_expense_categ_id"
            )
            rec.account_income_parent_id = my_parent_account(
                product, "property_account_income_categ_id"
            )
