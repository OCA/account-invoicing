# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import datetime
import logging
import re
from types import MethodType

from psycopg2 import sql
from psycopg2.extensions import AsIs

from .common import TestAccountInvoiceSectionPickingCommon

_logger = logging.getLogger(__name__)

try:
    from freezegun import freeze_time
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestAccountInvoiceSectionPickingBackorder(TestAccountInvoiceSectionPickingCommon):
    def setUp(self):
        super().setUp()
        self._monkey_patch_cursor_freeze_time()
        self.addCleanup(self._reset_monkey_patch_cursor_freezetime)

    def _reset_monkey_patch_cursor_freezetime(self):
        self.env.cr.execute = self.env.cr.standard_exec

    def _monkey_patch_cursor_freeze_time(self):
        """Monkey patch cursor to replace SQL TIME/DATE keywords"""
        # TODO: Extract this part into a fork of freezegun for odoo?
        # Copied from https://github.com/CloverHealth/pytest-pgsql/blob/1.1.2/pytest_pgsql/time.py#L12-L24  # noqa
        _TIMESTAMP_REPLACEMENT_FORMATS = (
            # Functions
            (
                r"\b((NOW|CLOCK_TIMESTAMP|STATEMENT_TIMESTAMP|TRANSACTION_TIMESTAMP)\s*\(\s*\))",  # noqa
                r"'{:%Y-%m-%d %H:%M:%S.%f %z}'::TIMESTAMPTZ",
            ),
            (
                r"\b(TIMEOFDAY\s*\(\s*\))",
                r"'{:%Y-%m-%d %H:%M:%S.%f %z}'::TEXT",
            ),
            # Keywords
            (r"\b(CURRENT_DATE)\b", r"'{:%Y-%m-%d}'::DATE"),
            (r"\b(CURRENT_TIME)\b", r"'{:%H:%M:%S.%f %z}'::TIMETZ"),
            (
                r"\b(CURRENT_TIMESTAMP)\b",
                r"'{:%Y-%m-%d %H:%M:%S.%f %z}'::TIMESTAMPTZ",
            ),
            (r"\b(LOCALTIME)\b", r"'{:%H:%M:%S.%f}'::TIME"),
            (r"\b(LOCALTIMESTAMP)\b", r"'{:%Y-%m-%d %H:%M:%S.%f}'::TIMESTAMP"),
        )

        self.env.cr.standard_exec = self.env.cr.execute

        def frozen_time_execute(self, query, params=None, log_exceptions=None):
            def replace_keywords(regex, replacement, timestamp, query):
                return re.sub(
                    regex,
                    replacement.format(timestamp),
                    query,
                    flags=re.IGNORECASE,
                )

            timestamp = datetime.datetime.now()
            for regex, replacement in _TIMESTAMP_REPLACEMENT_FORMATS:
                if isinstance(query, sql.Composed):
                    new_composed = []
                    for comp in query:
                        if isinstance(comp, sql.SQL):
                            comp = replace_keywords(
                                regex, replacement, timestamp, comp.string
                            )
                            new_composed.append(sql.SQL(comp))
                        else:
                            new_composed.append(comp)
                    query = sql.Composed(new_composed)
                else:
                    query = replace_keywords(regex, replacement, timestamp, query)
                if params is not None:
                    for i, param in enumerate(params):
                        if isinstance(param, AsIs):
                            new_param = AsIs(
                                replace_keywords(
                                    regex,
                                    replacement,
                                    timestamp,
                                    param.getquoted().decode(),
                                )
                            )
                            params[i] = new_param
            return self.standard_exec(
                query, params=params, log_exceptions=log_exceptions
            )

        self.env.cr.execute = MethodType(frozen_time_execute, self.env.cr)

    def test_group_by_delivery_picking_backorder_delivered_qties(self):
        self.product_1.invoice_policy = "delivery"
        with freeze_time("2021-12-10 10:00:00"):
            self.order_1.action_confirm()
        with freeze_time("2021-12-10 10:00:01"):
            self.order_2.action_confirm()
        with freeze_time("2021-12-10 10:00:02"):
            delivery_1_move = self.order_1.order_line.move_ids
            delivery_1_move.move_line_ids.qty_done = 2.0
            delivery_1 = delivery_1_move.picking_id

            backorder_wiz_action = delivery_1.button_validate()
            backorder_wiz = (
                self.env["stock.backorder.confirmation"]
                .with_context(**backorder_wiz_action.get("context"))
                .create({})
            )
            backorder_wiz.process()
        with freeze_time("2021-12-10 10:00:03"):
            delivery_1_backorder_move = (
                self.order_1.order_line.move_ids - delivery_1_move
            )
            delivery_1_backorder = delivery_1_backorder_move.picking_id
            delivery_2_move = self.order_2.order_line.move_ids
            delivery_2_move.move_line_ids.qty_done = 3.0
            delivery_2 = delivery_2_move.picking_id
            backorder_wiz_action = delivery_2.button_validate()
            backorder_wiz = (
                self.env["stock.backorder.confirmation"]
                .with_context(**backorder_wiz_action.get("context"))
                .create({})
            )
            backorder_wiz.process()
        with freeze_time("2021-12-10 10:00:04"):
            delivery_2_backorder_move = (
                self.order_2.order_line.move_ids - delivery_2_move
            )
            delivery_2_backorder = delivery_2_backorder_move.picking_id
            self.env["account.move"].flush([])
            invoice = (self.order_1 + self.order_2)._create_invoices()
            result = {
                10: (delivery_1.name, "line_section"),
                20: (self.order_1.order_line.name, False),
                30: (delivery_2.name, "line_section"),
                40: (self.order_2.order_line.name, False),
            }
            for line in invoice.invoice_line_ids.sorted("sequence"):
                self.assertEqual(line.name, result[line.sequence][0])
                self.assertEqual(line.display_type, result[line.sequence][1])
        with freeze_time("2021-12-10 10:00:05"):
            delivery_1_backorder.action_assign()
        with freeze_time("2021-12-10 10:00:06"):
            delivery_2_backorder.action_assign()
        with freeze_time("2021-12-10 10:00:07"):
            delivery_1_backorder_move.move_line_ids.qty_done = 3.0
            delivery_1_backorder.button_validate()
        with freeze_time("2021-12-10 10:00:08"):
            delivery_2_backorder_move.move_line_ids.qty_done = 2.0
            delivery_2_backorder.button_validate()
        with freeze_time("2021-12-10 10:00:09"):
            invoice_backorder = (self.order_1 + self.order_2)._create_invoices()
            result_backorder = {
                10: (delivery_1_backorder.name, "line_section"),
                20: (self.order_1.order_line.name, False),
                30: (delivery_2_backorder.name, "line_section"),
                40: (self.order_2.order_line.name, False),
            }
            for line in invoice_backorder.invoice_line_ids.sorted("sequence"):
                self.assertEqual(line.name, result_backorder[line.sequence][0])
                self.assertEqual(line.display_type, result_backorder[line.sequence][1])
