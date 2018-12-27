# -*- coding: utf-8 -*-
# @ 2018 Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestAccountInvoiceFromPicking(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceFromPicking, self).setUp()

        self.stock_picking_obj = self.env['stock.picking']
        self.stock_invoice_onshipping = self.env['stock.invoice.onshipping']
        self.stock_return_picking = self.env['stock.return.picking']
        self.stock_picking_1 = self.stock_picking_obj.browse(
            self.ref(
                'account_invoice_from_picking.test_invoice_from_picking_1')
        )
        self.stock_picking_2 = self.stock_picking_obj.browse(
            self.ref(
                'account_invoice_from_picking.test_invoice_from_picking_2')
        )
        self.stock_picking_3 = self.stock_picking_obj.browse(
            self.ref(
                'account_invoice_from_picking.test_invoice_from_picking_3')
        )
        self.stock_picking_4 = self.stock_picking_obj.browse(
            self.ref(
                'account_invoice_from_picking.test_invoice_from_picking_4')
        )

    def test_confirm_account_invoice_from_picking(self):
        self.stock_picking_1.action_confirm()
        for move in self.stock_picking_1.move_lines:
            self.assertEqual(
                move.state, 'confirmed', 'Wrong state of move line.'
            )
            self.assertEqual(
                move.invoice_state, '2binvoiced',
                'Wrong invoice state of move line.'
            )
        self.stock_picking_1.action_assign()
        self.stock_picking_1.do_prepare_partial()
        self.stock_picking_1.do_transfer()
        self.assertEqual(
            self.stock_picking_1.state, 'done',
            'Wrong state of outgoing shipment.')

        wizard_group_partner = self.stock_invoice_onshipping.with_context(
            active_ids=[self.stock_picking_1.id]
        ).create({
            'group': False,
            'journal_type': 'sale'
        })
        wizard_group_partner.open_invoice()

        invoice = self.env['account.invoice'].search([(
            'origin', '=', self.stock_picking_1.name
        )])
        self.assertTrue(invoice, 'Invoice is not created.')
        for line in invoice.invoice_line_ids:
            self.assertEquals(
                line.picking_id.id, self.stock_picking_1.id,
                'Relation between invoice line and picking are missing.')
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing.'
            )
        self.assertTrue(
            invoice.tax_line_ids, 'Total of Taxes in Invoice are missing.'
        )

        for move in self.stock_picking_1.move_lines:
            self.assertEqual(move.state, 'done', 'Wrong state of move line.')
            self.assertEqual(
                move.invoice_state, 'invoiced',
                'Wrong invoice state of move line.')
        self.assertEqual(
            self.stock_picking_1.invoice_state, 'invoiced',
            'Wrong invoice state of picking.')

    def test_create_acccout_invoices_grouping_from_picking(self):
        self.assertEqual(
            self.stock_picking_2.state, 'done',
            'Wrong state of outgoing shipment.')

        wizard_group_partner = self.stock_invoice_onshipping.with_context(
            active_ids=[self.stock_picking_2.id, self.stock_picking_3.id]
        ).create({
            'group': True,
            'journal_type': 'sale'
        })

        wizard_group_partner.open_invoice()

        invoice_origin = str(self.stock_picking_2.name) + ', ' +\
                         str(self.stock_picking_3.name)
        grouping_invoice = self.env['account.invoice'].search([(
            'origin', '=', invoice_origin
        )])
        self.assertTrue(
            grouping_invoice.tax_line_ids,
            'Total of Taxes in Invoice are missing.'
        )

        invoice_lines_2 = self.env['account.invoice.line'].search(
            [('picking_id', '=', self.stock_picking_2.id)])
        self.assertTrue(
            invoice_lines_2,
            'Error to create invoice line of Grouping Pickings.'
        )
        for line in invoice_lines_2:
            self.assertEquals(
                line.invoice_id.id, grouping_invoice.id,
                'Error to create invoice line of Grouping Pickings.'
            )
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing of Grouping Pickings.'
            )

        invoice_lines_3 = self.env['account.invoice.line'].search(
            [('picking_id', '=', self.stock_picking_3.id)])
        self.assertTrue(
            invoice_lines_3,
            'Error to create invoice line of Grouping Pickings.'
        )
        for line in invoice_lines_3:
            self.assertEquals(
                line.invoice_id.id, grouping_invoice.id,
                'Error to create invoice line of Grouping Pickings.'
            )
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing of Grouping Pickings.'
            )

        self.assertEqual(
            self.stock_picking_2.invoice_state, 'invoiced',
            'Wrong invoice state of picking.')
        self.assertEqual(
            self.stock_picking_3.invoice_state, 'invoiced',
            'Wrong invoice state of picking.')

    def test_create_account_invoice_from_picking_incoming(self):
        self.stock_picking_4.action_confirm()
        for move in self.stock_picking_4.move_lines:
            self.assertEqual(
                move.state, 'assigned', 'Wrong state of move line.'
            )
            self.assertEqual(
                move.invoice_state, '2binvoiced',
                'Wrong invoice state of move line.'
            )
        self.stock_picking_4.action_assign()
        self.stock_picking_4.do_prepare_partial()
        self.stock_picking_4.do_transfer()
        self.assertEqual(
            self.stock_picking_4.state, 'done',
            'Wrong state of outgoing shipment.')
        wizard_group_partner = self.stock_invoice_onshipping.with_context(
            active_ids=[self.stock_picking_4.id]
        ).create({
            'group': False,
            'journal_type': 'purchase'
        })
        wizard_group_partner.open_invoice()

        invoice = self.env['account.invoice'].search([(
            'origin', '=', self.stock_picking_4.name
        )])
        self.assertTrue(invoice, 'Invoice is not created of Incoming Picking.')
        for line in invoice.invoice_line_ids:
            self.assertEquals(
                line.picking_id.id, self.stock_picking_4.id,
                'Relation between invoice line and picking'
                ' are missing of Incoming Picking.')
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing'
                ' of Incoming Picking.'
            )
        self.assertTrue(
            invoice.tax_line_ids,
            'Total of Taxes in Invoice are missing of Incoming Picking .'
        )

        invoice_lines_4 = self.env['account.invoice.line'].search(
            [('picking_id', '=', self.stock_picking_4.id)])
        self.assertTrue(invoice_lines_4)
        for line in invoice_lines_4:
            self.assertEquals(
                line.invoice_id.id, invoice.id,
                'Error to create invoice line of Grouping Pickings.'
            )
            self.assertTrue(
                line.invoice_line_tax_ids,
                'Taxes in invoice lines are missing of Grouping Pickings.'
            )

        for move in self.stock_picking_4.move_lines:
            self.assertEqual(move.state, 'done', 'Wrong state of move line.')
            self.assertEqual(
                move.invoice_state, 'invoiced',
                'Wrong invoice state of move line.')
        self.assertEqual(
            self.stock_picking_4.invoice_state, 'invoiced',
            'Wrong invoice state of picking.')

    def test_create_account_invoice_from_return_picking(self):
        wizard_stock_return_picking = self.stock_return_picking.with_context(
            active_ids=[self.stock_picking_2.id],
            active_id=self.stock_picking_2.id
        ).create({
            'invoice_state': '2binvoiced',
        })
        result = wizard_stock_return_picking._create_returns()
        return_picking_obj = self.stock_picking_obj.browse(result[0])
        self.assertEqual(
            return_picking_obj.invoice_state, '2binvoiced',
            'Wrong invoice state of picking.')
        self.assertEqual(
            return_picking_obj.origin, self.stock_picking_2.name,
            'Wrong value for field origin in created returned picking.')
