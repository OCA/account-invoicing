# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

GROUP_XML_ID = 'account_invoice_check_total.group_supplier_inv_check_total'


class AccountConfigSettings(models.Model):

    _inherit = 'account.config.settings'

    group_supplier_inv_check_total = fields.Boolean(
        string="Check Total on Vendor Bills",
        implied_group=GROUP_XML_ID)
