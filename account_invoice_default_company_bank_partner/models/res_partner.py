# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_company_bank_id = fields.Many2one(
        'res.partner.bank', string='Default Company Bank')
