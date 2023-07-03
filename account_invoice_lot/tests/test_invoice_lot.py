# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInvoiceLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_order_lot_selection.sale1")
        cls.lot = cls.env.ref("sale_order_lot_selection.lot_cable")

    def test_propagate_serial_number_on_invoice_line(self):
        self.sale.action_confirm()
        self.invoice = self.sale._create_invoices()
        invoice_lots = self.sale.order_line.invoice_lines.mapped("lot_id")
        self.assertIn(self.lot, invoice_lots)
