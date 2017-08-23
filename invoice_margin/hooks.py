# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def _create_column(cr, table_name, column_name, column_type):
    req = "ALTER TABLE %s ADD COLUMN %s %s" % (
        table_name, column_name, column_type)
    cr.execute(req)


def pre_init_hook(cr):
    _logger.info(
        "Compute account_invoice_line.purchase_price for existing lines")
    _create_column(cr, 'account_invoice_line', 'purchase_price', 'numeric')
    cr.execute("""
        UPDATE account_invoice_line
            SET purchase_price = line_standard_price.standard_price
        FROM (
            SELECT
                ail.id line_id,
                (SELECT cost
                    FROM product_price_history pph
                    WHERE(
                            ai.date_invoice is null
                            OR date_trunc('day', pph.datetime) <=
                                ai.date_invoice)
                        AND pph.product_template_id = pp.product_tmpl_id
                        AND pph.company_id = ail.company_id
                    ORDER BY datetime desc
                    LIMIT 1) standard_price
            FROM account_invoice_line ail
            INNER JOIN account_invoice ai
                ON ai.id = ail.invoice_id
            INNER JOIN product_product pp
                ON pp.id = ail.product_id
            ) line_standard_price
        WHERE
            account_invoice_line.id = line_standard_price.line_id;
        """)

    _logger.info(
        "Fast Compute account_invoice_line fields: margin, margin_percent")
    _create_column(cr, 'account_invoice_line', 'margin', 'numeric')
    _create_column(cr, 'account_invoice_line', 'margin_percent', 'numeric')
    cr.execute("""
        UPDATE account_invoice_line
        SET
            margin = price_subtotal - (purchase_price * quantity),
            margin_percent = CASE
                WHEN price_subtotal = 0 then 0
                ELSE 100 * (price_subtotal - (purchase_price * quantity))
                    / price_subtotal
                END;
        """)

    _logger.info("Fast Compute account_invoice fields: margin, margin_percent")
    _create_column(cr, 'account_invoice', 'margin', 'numeric')
    _create_column(cr, 'account_invoice', 'margin_percent', 'numeric')
    cr.execute("""
        UPDATE account_invoice ai
            SET
                margin = invoice_margin.margin,
                margin_percent = invoice_margin.margin_percent
        FROM (
            SELECT
                ai.id invoice_id,
                sum(ail.margin) margin,
                CASE
                    WHEN sum(ail.price_subtotal) = 0 THEN 0
                    ELSE sum(ail.margin) / sum(ail.price_subtotal) * 100
                    END margin_percent
            FROM account_invoice ai
            INNER JOIN account_invoice_line ail
                ON ail.invoice_id = ai.id
            GROUP BY ai.id
        ) invoice_margin
        WHERE ai.id = invoice_margin.invoice_id;
        """)
