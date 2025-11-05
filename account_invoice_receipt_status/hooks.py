# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# flake8: noqa B950

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):

    if sql.column_exists(cr, "account_move", "receipt_status"):
        return
    _logger.info("Adding receipt_status columns to account_move and account_move_line")
    cr.execute(
        """
        ALTER TABLE account_move
        ADD COLUMN receipt_status VARCHAR;
        """
    )
    cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN receipt_status VARCHAR;
        """
    )
    _logger.info("Initializing receipt_status columns in account_move_line")
    cr.execute(
        """
        UPDATE account_move_line aml
        SET receipt_status = pol.line_receipt_status
        FROM purchase_order_line pol
        WHERE aml.purchase_line_id = pol.id;
        """
    )
    _logger.info("%d account_move_line receipt_status updated", cr.rowcount)
    _logger.info("Initializing receipt_status columns in account_move")
    cr.execute(
        """
        UPDATE
            account_move m
        SET
            receipt_status = t.result
        FROM (
            SELECT
                aml.move_id,
                CASE
                    WHEN array_agg(aml.receipt_status) FILTER (WHERE aml.receipt_status IS NOT NULL) IS NULL
                    THEN NULL

                    WHEN (
                        array_agg(aml.receipt_status) FILTER (WHERE aml.receipt_status IS NOT NULL)
                            @> ARRAY['full']::varchar[]
                        AND NOT (
                            array_agg(aml.receipt_status) FILTER (WHERE aml.receipt_status IS NOT NULL)
                            && ARRAY['partial','pending']::varchar[]
                        )
                    )
                    THEN 'full'

                    WHEN (
                        array_agg(aml.receipt_status) FILTER (WHERE aml.receipt_status IS NOT NULL)
                            = ARRAY['pending']::varchar[]
                    )
                    THEN 'pending'

                    ELSE 'partial'
                END AS result
            FROM account_move_line aml
            WHERE aml.display_type NOT IN ('line_note','line_section')
            GROUP BY aml.move_id
        ) AS t
        WHERE
            m.id = t.move_id
            AND m.move_type = 'in_invoice';
        """
    )
    _logger.info("%d account_move receipt_status updated", cr.rowcount)
