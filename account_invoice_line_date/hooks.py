# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
try:
    from openupgradelib.openupgrade import add_fields
except (ImportError, IOError) as err:
    _logger.debug(err)


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fields_list = [(
        'date_invoice',
        'account.invoice.line',
        False,
        'date',
        'date',
        'account_invoice_line_date',
    )]
    add_fields(env, fields_list)
    cr.execute("""
        UPDATE account_invoice_line
        SET date_invoice = ai.date_invoice
        FROM account_invoice AS ai
        WHERE ai.id = account_invoice_line.invoice_id
        AND ai.date_invoice IS NOT NULL
    """)
