# -*- coding: utf-8 -*-
# © 2011 Domsense s.r.l. (<http://www.domsense.com>).
# © 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
# © 2016 Farid Shahy (<fshahy@gmail.com>)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    address_shipping_id = fields.Many2one(
        'res.partner',
        'Shipping Address',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        help="Delivery address for current invoice."
    )
