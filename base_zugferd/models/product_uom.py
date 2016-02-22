# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductUom(models.Model):
    _inherit = 'product.uom'

    zugferd_code = fields.Char(string='ZUGFeRD Code', size=3)
