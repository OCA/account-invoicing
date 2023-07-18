import logging

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
    moves.with_context(tracking_disable=True)._compute_pricelist_id()
