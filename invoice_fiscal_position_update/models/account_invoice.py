# -*- coding: utf-8 -*-
# Copyright 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014 Akretion (http://www.akretion.com)
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('fiscal_position_id')
    def onchange_fiscal_position_id(self):
        """Updates taxes and accounts on all invoice lines"""
        self.ensure_one()
        res = {}
        lines_without_product = []
        fp = self.fiscal_position_id
        inv_type = self.type
        company_id = self.company_id or self.env.user.company_id
        for line in self.invoice_line_ids:
            if line.product_id:
                product = line.product_id
                if inv_type in ('out_invoice', 'out_refund'):
                    account = (
                        product.property_account_income_id or
                        product.categ_id.property_account_income_categ_id)
                    taxes = product.taxes_id.filtered(
                        lambda r: r.company_id == company_id)

                else:
                    account = (
                        product.property_account_expense_id or
                        product.categ_id.property_account_expense_categ_id)
                    taxes = product.supplier_taxes_id.filtered(
                        lambda r: r.company_id == company_id)
                taxes = taxes or account.tax_ids
                if fp:
                    account = fp.map_account(account)
                    taxes = fp.map_tax(taxes).filtered(
                        lambda r: r.company_id == company_id)

                line.invoice_line_tax_ids = [(6, 0, taxes.ids)]
                line.account_id = account.id
            else:
                lines_without_product.append(line.name)

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(self.invoice_line):
                res['warning']['message'] = _(
                    "The invoice lines were not updated to the new "
                    "Fiscal Position because they don't have products.\n"
                    "You should update the Account and the Taxes of each "
                    "invoice line manually.")
            else:
                res['warning']['message'] = _(
                    "The following invoice lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n- %s\nYou should update the Account and the "
                    "Taxes of these invoice lines manually."
                ) % ('\n- '.join(lines_without_product))
        return res
