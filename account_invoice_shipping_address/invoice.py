# -*- coding: utf-8 -*-
# Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
# Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# Copyright 2017 Apulia Software srl - www.apuliasoftware.it
# Author Andrea Cometa <a.cometa@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    address_shipping_id = fields.Many2one(
        'res.partner', 'Shipping Address',
        readonly=True, states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]},
        help="Delivery address for current invoice.")
