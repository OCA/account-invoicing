# -*- coding: utf-8 -*-
# Copyright 2016 Davide Corio (Abstract)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class SequentialDatesCase(TransactionCase):

    def setUp(self):
        super(SequentialDatesCase, self).setUp()
        self.partner1 = self.env['res.partner'].create({'name': 'Partner1'})

    def test_create_invoice(self):
        invoice_model = self.env['account.invoice']
        invoice = invoice_model.search(
            [('type', '=', 'out_invoice'), ('state', '=', 'open')], limit=1)
        new_invoice = invoice.copy()
        new_invoice.date_invoice = datetime.strptime(
            invoice.date_invoice, '%Y-%m-%d') - timedelta(days=1)
        with self.assertRaises(ValidationError):
            new_invoice.action_invoice_open()
