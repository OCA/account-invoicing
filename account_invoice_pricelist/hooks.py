import logging

from psycopg2.extras import execute_values

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    """Precreate pricelist_id column to prevent tracked computation."""
    logger = logging.getLogger(__name__)
    logger.info("Add account_move.financial_type column if it does not yet exist")
    cr.execute("ALTER TABLE account_move ADD COLUMN IF NOT EXISTS pricelist_id int4")


def post_init_hook(cr, registry):
    """Fill pricelist_id without tracking."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    moves = env["account.move"].search(
        [("move_type", "in", ("out_invoice", "out_refund"))]
    )
    vals = []
    for invoice in moves:
        if invoice.partner_id and invoice.partner_id.property_product_pricelist:
            vals.append((invoice.id, invoice.partner_id.property_product_pricelist.id))
    if vals:
        execute_values(
            cr,
            """
            UPDATE account_move SET pricelist_id = vals.p
            FROM (VALUES %s) AS vals (id, p)
            WHERE account_move.id = vals.id
            """,
            vals,
        )
