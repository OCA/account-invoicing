# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import odoo

_logger = logging.getLogger(__name__)


def update_draft_invoice_blocked_field_value(env):
    env.cr.execute("""
        UPDATE account_invoice
        SET blocked = draft_blocked
        WHERE state = 'draft'
    """)


def update_open_invoice_blocked_field_value(env):
    query = """
        SELECT ai.id as inv_id, aml.id as aml_id, aml.blocked
        FROM account_move_line aml
        LEFT JOIN account_invoice ai on aml.invoice_id = ai.id
        LEFT JOIN account_account aa on aa.id = aml.account_id
        LEFT JOIN account_account_type aat on aat.id = aa.user_type_id
        WHERE aat.type in %s
        ORDER BY ai.id
    """
    types = ('receivable', 'payable')
    env.cr.execute(query, [types])
    rows = env.cr.fetchall()

    current_inv_id = None

    blocked_by_invoice_ids = {}
    invoice_ids_to_block = []

    for row in rows:
        inv_id = row[0]

        if inv_id != current_inv_id and current_inv_id is not None:
            if all(blocked_by_invoice_ids[current_inv_id]):
                invoice_ids_to_block.append(current_inv_id)

        if inv_id not in blocked_by_invoice_ids:
            blocked_by_invoice_ids[inv_id] = []
        blocked_by_invoice_ids[inv_id].append(row[2])
        current_inv_id = inv_id

    if all(blocked_by_invoice_ids[current_inv_id]):
        invoice_ids_to_block.append(current_inv_id)

    if invoice_ids_to_block:
        update_query = """
            UPDATE account_invoice
            SET blocked = TRUE
            WHERE id
        """

        if len(invoice_ids_to_block) == 1:
            update_query += ' = %s'
            args = (invoice_ids_to_block[0],)
        else:
            update_query += ' in %s'
            args = (tuple(invoice_ids_to_block),)

        env.cr.execute(update_query, args)


def migrate(cr, version):
    if not version:
        # installation of the module
        return
    with odoo.api.Environment.manage():
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        update_draft_invoice_blocked_field_value(env)
        update_open_invoice_blocked_field_value(env)
