# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging


def post_init_hook(cr, registry):
    """
    Post-install script. Because 'picking_ids' has been replaced by
    'related_picking_ids, we should be able to retrieve its values
    from the cursor. We use those to fill the new fields.
    """
    logging.getLogger('stock_picking_invoice_product_group').info(
        'Migrating existing related pickings')

    cr.execute("INSERT INTO account_invoice_stock_picking_rel"
               "(account_invoice_id, stock_picking_id) "
               "(SELECT invoice_id, id FROM "
               "stock_picking "
               "WHERE invoice_id IS NOT NULL)")
