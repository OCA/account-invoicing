# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    date_invoice = fields.Date(
        related="invoice_id.date_invoice",
        store=True,
    )
