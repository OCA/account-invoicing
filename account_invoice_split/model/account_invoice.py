# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################
import logging

from openerp.osv import orm, fields
from openerp.tools.translate import _

logger = logging.getLogger(__name__)


class account_invoice_line(orm.Model):
    ''' Adds a field for moving a line to a new invoice'''
    _inherit = "account.invoice.line"

    def _get_split_line(self, cr, uid, ids, field_name, args, context=None):
        """Boolean value telling that the invoice line will be moved to
        another invoice. It is set to true if the invoice_line is
        currently attached to no invoice."""
        return {invl.id: not invl.invoice_id for invl in self.browse(
            cr, uid, ids, context)}

    def _write_lines(self, cr, uid, ids, field_name, field_value, arg,
                     context):
        # The line will be moved by the split_wizard object.
        return True

    _columns = {
        'split': fields.function(
            _get_split_line, fnct_inv=_write_lines, type='boolean',
            string=_('Put line into new invoice'))
    }
