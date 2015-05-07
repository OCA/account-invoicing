# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alex Comba <alex.comba@agilebg.com>
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm


class stock_config_settings(orm.TransientModel):
    _inherit = 'stock.config.settings'

    _columns = {
        'group_not_use_picking_name_per_invoice_line': fields.boolean(
            "Not add picking name on invoice lines",
            implied_group="invoice_line_no_picking_name."
            "group_not_use_picking_name_per_invoice_line",
            help="Allows you to not use the picking name on the invoice lines."
                 " The picking name is added to invoice lines when you "
                 "generate 1 invoice from more than 1 picking"
        ),
    }
