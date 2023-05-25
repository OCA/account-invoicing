# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import tagged
from odoo.tools import float_is_zero

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestClearingWizard(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.cl_partner = cls.env["res.partner"].create(
            {
                "name": "Clearing Partner",
                "is_company": True,
                "child_ids": [
                    (0, 0, {"name": "Clearing Contact 1", "type": "invoice"}),
                    (0, 0, {"name": "Clearing Contact 2", "type": "invoice"}),
                ],
            }
        )

    def test_clearing_wizard(self):
        """Test clearing wizard with different move types."""

        def sorted_by_sequence(lines):
            return sorted(lines, key=lambda l: l.sequence)

        move_types = ["out_invoice", "in_invoice"]
        for init_move_type, clearing_move_type in [move_types, move_types[::-1]]:
            with self.subTest(
                init_move_type=init_move_type, clearing_move_type=clearing_move_type
            ):
                init_inv = self.init_invoice(
                    invoice_date=fields.Date.today(),
                    move_type=init_move_type,
                    partner=self.cl_partner,
                    amounts=[100, 200],
                    post=True,
                )
                cl_inv_1 = self.init_invoice(
                    invoice_date=fields.Date.today() + timedelta(days=5),
                    move_type=clearing_move_type,
                    partner=self.cl_partner.child_ids[0],
                    amounts=[100],
                    post=True,
                )
                cl_inv_2 = self.init_invoice(
                    invoice_date=fields.Date.today() + timedelta(days=10),
                    move_type=clearing_move_type,
                    partner=self.cl_partner.child_ids[1],
                    amounts=[200],
                    post=True,
                )
                # Create wizard
                cw_action = init_inv.action_open_invoice_clearing_wizard()
                wizard = self.env[cw_action["res_model"]].browse(cw_action["res_id"])
                # Test Action: Unlink Lines
                wizard.action_unlink_lines()
                self.assertFalse(wizard.line_ids)
                # Test Action: Add Lines
                wizard.action_add_lines()
                self.assertTrue(wizard.line_ids)
                # Test Action: Sort Lines by Date Due
                wizard.action_sort_by_date_due_asc()
                slines = sorted_by_sequence(wizard.line_ids)
                self.assertTrue(slines[0].date_maturity < slines[1].date_maturity)
                wizard.action_sort_by_date_due_desc()
                slines = sorted_by_sequence(wizard.line_ids)
                self.assertTrue(slines[0].date_maturity > slines[1].date_maturity)
                # Test Action: Sort Lines by Amount Residual
                wizard.action_sort_by_residual_asc()
                slines = sorted_by_sequence(wizard.line_ids)
                self.assertTrue(slines[0].amount_residual < slines[1].amount_residual)
                wizard.action_sort_by_residual_desc()
                slines = sorted_by_sequence(wizard.line_ids)
                self.assertTrue(slines[0].amount_residual > slines[1].amount_residual)
                # Test Action: Fill Amount to Clear
                wizard.action_fill_amount_to_clear()
                wizard.refresh()
                self.assertTrue(
                    float_is_zero(
                        wizard.amount_to_clear,
                        precision_rounding=wizard.company_currency_id.rounding,
                    )
                )
                # Test Action: Reset Lines
                wizard.action_reset_lines()
                wizard.refresh()
                self.assertTrue(
                    not float_is_zero(
                        wizard.amount_to_clear,
                        precision_rounding=wizard.company_currency_id.rounding,
                    )
                )
                # Create moves
                wizard.action_fill_amount_to_clear()
                wizard.refresh()
                wizard.button_confirm()
                self.assertEqual(init_inv.payment_state, "paid")
                self.assertEqual(cl_inv_1.payment_state, "paid")
                self.assertEqual(cl_inv_2.payment_state, "paid")

    def test_internal_types(self):
        aicw_model = self.env["account.invoice.clearing.wizard"]
        # For lines to clear
        self.assertEqual(
            "payable",
            aicw_model._get_internal_type_from_move_type(
                "in_invoice", is_counterpart=False
            ),
        )
        self.assertEqual(
            "receivable",
            aicw_model._get_internal_type_from_move_type(
                "out_invoice", is_counterpart=False
            ),
        )
        # For counterpart lines
        self.assertEqual(
            "receivable",
            aicw_model._get_internal_type_from_move_type(
                "in_invoice", is_counterpart=True
            ),
        )
        self.assertEqual(
            "payable",
            aicw_model._get_internal_type_from_move_type(
                "out_invoice", is_counterpart=True
            ),
        )
