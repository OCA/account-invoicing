# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def add_invoice_blocked_column(cr):
    # Create the column to prevent field to compute.
    cr.execute("""
    DO $$
        BEGIN
            ALTER TABLE account_invoice
            ADD COLUMN blocked BOOLEAN DEFAULT FALSE;
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'blocked already exists';
        END;
    $$
    """)


def migrate(cr, version):
    add_invoice_blocked_column(cr)
