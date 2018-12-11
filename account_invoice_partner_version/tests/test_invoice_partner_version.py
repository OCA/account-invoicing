# -*- coding: utf-8 -*-
# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInvoicePartnerVersion(TransactionCase):

    def setUp(self):
        super(TestInvoicePartnerVersion, self).setUp()
        self.invoice = self.env['account.invoice'].search(
            [('state', '=', 'draft')])[0]

    def test_invoice_version_partner(self):
        self.assertFalse(self.invoice.partner_id.version_hash)
        self.invoice.action_invoice_open()
        self.assertTrue(self.invoice.partner_id.version_hash)
