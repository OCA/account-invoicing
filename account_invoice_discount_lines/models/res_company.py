# coding: utf-8
# Copyright 2017 Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    discount_product = fields.Many2one(
        'product.product',
        help=('Product that is applied to invoice lines on which the amount of'
              ' discount is transferred upon invoice validation'))
