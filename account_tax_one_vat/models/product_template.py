# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "one.vat.mixin"]

    vat_id = fields.Many2one(
        "account.tax",
        compute="_compute_product_vat",
        string="VAT",
    )
    vat = fields.Char(compute="_compute_product_vat", string="VAT name")

    @api.constrains("taxes_id")
    def _check_only_one_vat_customer_tax(self):
        self._check_only_one_vat_tax_field("taxes_id")

    @api.onchange("taxes_id")
    def _onchange_only_one_vat_customer_tax(self):
        self._onchange_one_vat_tax_field("taxes_id")

    @api.constrains("supplier_taxes_id")
    def _check_only_one_vat_supplier_tax(self):
        self._check_only_one_vat_tax_field("supplier_taxes_id")

    @api.onchange("supplier_taxes_id")
    def _onchange_only_one_vat_supplier_tax(self):
        self._onchange_one_vat_tax_field("supplier_taxes_id")

    @api.depends("taxes_id", "company_id")
    @api.depends_context("company")
    def _compute_product_vat(self):
        loggedin_company = self.env.company
        for rec in self:
            vat = rec.taxes_id.filtered(
                lambda r: r.is_vat and r.company_id == loggedin_company
            )
            rec.vat_id = vat if loggedin_company.account_tax_one_vat else False
            rec.vat = (
                vat.name if vat and loggedin_company.account_tax_one_vat else False
            )
