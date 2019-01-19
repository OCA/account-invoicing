# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo.exceptions import UserError


class TestCorrispettivi(AccountingTestCase):

    def setUp(self):
        super(TestCorrispettivi, self).setUp()
        partner_model = self.env['res.partner']
        self.fiscal_pos_model = self.env['account.fiscal.position']
        self.journal_model = self.env['account.journal']
        self.invoice_model = self.env['account.invoice']
        self.corr_fiscal_position = self.fiscal_pos_model.create({
            'name': 'corrispettivi fiscal position',
            'corrispettivi': True,
            'company_id': self.env.user.company_id.id
        })
        self.no_corr_fiscal_position = self.fiscal_pos_model.create({
            'name': 'corrispettivi fiscal position',
            'corrispettivi': False,
            'company_id': self.env.user.company_id.id
        })
        self.corrispettivi_partner = partner_model.create({
            'name': 'Corrispettivi partner',
            'use_corrispettivi': True,
            'property_account_position_id': self.corr_fiscal_position.id
        })
        self.no_corrispettivi_partner = partner_model.create({
            'name': 'Corrispettivi partner',
            'use_corrispettivi': False,
            'property_account_position_id': self.no_corr_fiscal_position.id
        })

        self.account_receivable = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)

    def create_corr_journal(self):
        corr_journal_id = self.env['account.journal'].create({
            'name': 'CORR',
            'code': 'CORR',
            'type': 'sale',
            'corrispettivi': True
        })
        return corr_journal_id

    def create_corrispettivi_invoice(self):
        corr_invoice = self.invoice_model \
            .with_context(default_corrispettivi=True) \
            .create({'account_id': self.account_receivable.id})
        return corr_invoice

    def test_get_corr_journal(self):
        """ Test that get_corr_journal gets a corrispettivi journal
        or raises an UserError if none found"""
        corr_journal_id = self.journal_model.get_corr_journal()
        self.assertEqual(corr_journal_id.type, 'sale')
        self.assertTrue(corr_journal_id.corrispettivi)

        corr_journal_id.unlink()
        with self.assertRaises(UserError):
            self.journal_model.get_corr_journal()

    def test_get_corr_fiscal_pos(self):
        """ Test that get_corr_fiscal_pos gets a corrispettivi fiscal
        position"""
        corr_fiscal_pos = self.fiscal_pos_model.get_corr_fiscal_pos()
        self.assertTrue(corr_fiscal_pos.corrispettivi)

    def test_corrispettivi_partner_onchange(self):
        """ Test onchange in partner. """
        # If the partner uses corrispettivi,
        # the fiscal position must have the flag corrispettivi
        self.corrispettivi_partner.onchange_use_corrispettivi()
        self.assertTrue(self.corrispettivi_partner
                        .property_account_position_id.corrispettivi)

        # If the partner does not use corrispettivi
        # and it already has a fiscal position that is corrispettivi,
        # it must be removed
        self.no_corrispettivi_partner.write({
            'property_account_position_id': self.corr_fiscal_position.id})
        self.no_corrispettivi_partner.onchange_use_corrispettivi()
        self.assertFalse(
            self.no_corrispettivi_partner.property_account_position_id)

        # If the partner does not use corrispettivi
        # and it already has a fiscal position that is not corrispettivi,
        # it must not be removed
        self.no_corrispettivi_partner.write({
            'property_account_position_id': self.no_corr_fiscal_position.id})
        self.no_corrispettivi_partner.onchange_use_corrispettivi()
        self.assertEqual(
            self.no_corrispettivi_partner.property_account_position_id,
            self.no_corr_fiscal_position)

    def test_corrispettivi_invoice_default(self):
        """ Test default values for invoice. """
        corr_journal_id = self.create_corr_journal()
        corr_invoice = self.create_corrispettivi_invoice()
        self.assertEqual(
            corr_invoice.partner_id.id,
            self.env.ref('base.public_user').partner_id.id)
        self.assertEqual(
            corr_invoice.journal_id.id,
            corr_journal_id.id)

    def test_invoice_creation(self):
        """ Test invoice creation. """
        # if no corrispettivi journal exists, raise
        # No journal found for corrispettivi
        with self.assertRaises(UserError):
            self.invoice_model \
                .with_context(default_corrispettivi=True) \
                .create({'account_id': self.account_receivable.id})
        self.create_corr_journal()
        corr_invoice = self.create_corrispettivi_invoice()
        self.assertTrue(corr_invoice)

    def test_corrispettivo_print_sent(self):
        """ Test corrispettivo report. """
        corr_invoice = self.create_corrispettivi_invoice()
        corr_invoice.corrispettivo_print()
        self.assertTrue(corr_invoice.sent)

    def test_corrispettivi_invoice_onchange(self):
        """ Test onchange methods for invoice. """
        corr_journal_id = self.create_corr_journal()
        corr_invoice = self.create_corrispettivi_invoice()
        no_corr_journal = self.env['account.journal'].search(
            [('corrispettivi', '=', False)], limit=1)
        corr_invoice.write({
            'partner_id': self.corrispettivi_partner.id,
            'journal_id': no_corr_journal.id})
        corr_invoice.onchange_partner_id_corrispettivi()
        self.assertEqual(
            corr_invoice.journal_id.id,
            corr_journal_id.id)
