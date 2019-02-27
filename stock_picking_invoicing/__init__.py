# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from psycopg2.extensions import AsIs
from . import models
from . import wizards
_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    Remove views who exists into previous version but not into this one
    :param cr: database cursor
    :return:
    """
    _logger.info("Remove previous views which doesn't exist anymore "
                 "in this version")
    main_query = """
    SELECT res_id
    FROM ir_model_data
    WHERE name = 'stock_picking_invoice_out_form' AND
    module = 'stock_picking_invoicing' AND
    model = 'ir.ui.view'"""
    # Remove the view
    query_view = """
    DELETE FROM ir_ui_view
    WHERE id IN (%(main_query)s);"""
    # Remove the XML ID of the view
    query_data = """
    DELETE FROM ir_model_data
    WHERE res_id IN (%(main_query)s)
    AND model = 'ir.ui.view';"""
    values = {
        'main_query': AsIs(main_query),
    }
    cr.execute(query_view, values)
    cr.execute(query_data, values)
    _logger.info("Finished successfully")
