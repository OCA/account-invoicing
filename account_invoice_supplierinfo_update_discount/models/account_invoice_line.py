# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _is_correct_partner_info(self, partnerinfo):
        res = super(AccountInvoiceLine, self)._is_correct_partner_info(
            partnerinfo)
        return res and (self.discount == partnerinfo.discount)

    @api.multi
    def _prepare_supplier_wizard_line(self, supplierinfo, partnerinfo):
        res = super(AccountInvoiceLine, self)._prepare_supplier_wizard_line(
            supplierinfo, partnerinfo)
        res['current_discount'] = partnerinfo and partnerinfo.discount or False
        res['new_discount'] = self.discount
        return res
