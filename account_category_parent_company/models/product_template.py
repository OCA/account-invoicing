from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_accounts(self):
        super()._get_product_accounts()
        company = self.env.company.parent_id or self.env.company

        def my_categ_account_or_my_categ_parent_account(myfield):
            return self.categ_id[myfield] or self.with_company(
                company.id
            )._get_category_account(myfield)

        return {
            "income": self.property_account_income_id
            or my_categ_account_or_my_categ_parent_account(
                "property_account_income_categ_id"
            ),
            "expense": self.property_account_expense_id
            or my_categ_account_or_my_categ_parent_account(
                "property_account_expense_categ_id"
            ),
        }
