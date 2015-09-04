# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.cr_context
    def _auto_init(self, cr, context=None):
        """ hack: pre-create and initialize the picking_policy column so that
        the constraint setting will not fail, this is a hack, made necessary
        because Odoo tries to set the not-null constraint before
        applying default values """
        self._field_create(cr, context=context)
        column_data = self._select_column_data(cr)
        if 'picking_policy' not in column_data:
            default_picking_policy = 'picking_policy'
            if default_picking_policy:
                cr.execute("""ALTER TABLE "{table}" ADD COLUMN
                    "picking_policy"
                    character varying""".format(table=self._table))
                cr.execute("""UPDATE "{table}" SET
                    picking_policy='direct'""".
                           format(table=self._table))
        return super(SaleOrder, self)._auto_init(cr, context=context)
