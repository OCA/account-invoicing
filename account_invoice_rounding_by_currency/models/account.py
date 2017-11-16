# -*- coding: utf-8 -*-
# Copyright 2015 Alessio Gerace <alessio.gerace@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _compute_swedish_rounding(self, cr, uid, invoice, context=None):
        """
        Depending on the method defined, we add an invoice line or adapt the
        tax lines to have a rounded total amount on the invoice
        :param invoice: invoice browse record
        :return dict: updated values for _amount_all
        """
        # avoid recusivity

        if 'swedish_write' in context:
            return {}
        rounding_rule_model = self.pool.get('company.rounding')
        company = invoice.company_id
        if invoice.currency_id.id != company.currency_id.id:
            ret_ids = rounding_rule_model.search(
                cr, uid,
                [
                    ('company_id', '=', company.id),
                    ('currency_id', '=', invoice.currency_id.id),
                ],
                context=context)
            if ret_ids:
                rule = rounding_rule_model.browse(
                    cr, uid, ret_ids[0], context=context)
                company.tax_calculation_rounding_method = (
                    rule.tax_calculation_rounding_method)
                company.tax_calculation_rounding = (
                    rule.tax_calculation_rounding)
                company.tax_calculation_rounding_account_id = (
                    rule.tax_calculation_rounding_account_id)
            else:
                return {}

        return super(AccountInvoice, self)._compute_swedish_rounding(
            cr, uid, invoice, context=context)
