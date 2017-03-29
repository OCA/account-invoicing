# -*- coding: utf-8 -*-
# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    account_analytic_user_id = fields.Many2one('res.users',
                                               string='Project Manager',
                                               store=True,
                                               readonly=True)
