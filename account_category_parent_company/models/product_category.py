from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_accounts(self):
        super()._get_product_accounts()
        parent_company = self.env.company.parent_id or self.env.company
        return {
            "income": self.property_account_income_id
            or self.with_company(parent_company.id)._get_category_account(
                "property_account_income_categ_id"
            ),
            "expense": self.property_account_expense_id
            or self.with_company(parent_company.id)._get_category_account(
                "property_account_expense_categ_id"
            ),
        }
