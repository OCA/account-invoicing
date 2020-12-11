# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from odoo import _
from odoo.exceptions import UserError, ValidationError

from ..models.account import INVOICE_TYPES


class TestAccountApprovalProcess(AccountingTestCase):
    def setUp(self):
        super().setUp()

        self.msg_1 = _(
            "One or more invoice do not require approval.\nInvoices (ids):\n{ids}"
        )
        self.msg_2 = _(
            "Invoices must be in draft state in order to approve it.\nInvoices:\n{ids}"
        )
        self.msg_3 = _("The field 'Amount (from)' must be positive.")
        self.msg_4 = _("The field 'Amount (to)' must be positive or -1 for unlimited.")
        self.msg_5 = _(
            "The field 'Amount (to)' must be greater than the field 'Amount (from)'."
        )
        self.msg_6 = _(
            "At least one step of the type '{type}' must have the value -1 for "
            "unlimited at the field 'Amount (to)'."
        )
        self.msg_7 = _(
            "A type is not allowed; only the following types are permitted for journal "
            "'{journal}':\n{types}"
        )
        self.msg_8 = _(
            "You have no rights to approval one or more invoices.\nInvoices (ids):\n"
            "{ids}"
        )
        self.msg_9 = _(
            "One or more invoice do require approval.\nInvoices (ids):\n{ids}"
        )

        self.account_expense = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_expenses").id,
                )
            ],
            limit=1,
        )
        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )

        product = self.env.ref("product.product_product_8")  # iMac $ 1299
        self.invoice_type = "in_invoice"

        self.vendor_bill = self.env["account.invoice"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "type": self.invoice_type,
                "account_id": self.account_receivable.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.display_name,
                            "quantity": 1.0,
                            "price_unit": product.standard_price,
                            "account_id": self.account_expense.id,
                        },
                    ),
                ],
            }
        )
        process_fields = self.env["account.approval.process"].fields_get()
        self.vendor_bill_type_str = dict(
            process_fields["invoice_type"]["selection"]
        ).get(self.invoice_type)

        self.vendor_bill._onchange_partner_id()

        self.vendor_bill.invoice_line_ids._onchange_product_id()
        self.vendor_bill.invoice_line_ids._onchange_account_id()

    def test_00_no_levels(self):
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")

        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

    def test_01_progressbar(self):
        aap_obj = self.env["account.approval.process"]
        step_1 = aap_obj.create(
            {
                "invoice_type": self.invoice_type,
                "company_id": self.env.user.company_id.id,
                "name": "Test 1",
                "validation_amount_from": 0,
                "user_ids": [(4, self.env.ref("base.user_root").id)],
            }
        )
        step_2 = aap_obj.create(
            {
                "invoice_type": self.invoice_type,
                "company_id": self.env.user.company_id.id,
                "name": "Test 2",
                "validation_amount_from": 0,
                "user_ids": [(4, self.env.ref("base.user_root").id)],
            }
        )

        self.assertEqual(self.vendor_bill.approval_process_progress_current_step, 0)
        self.assertEqual(self.vendor_bill.approval_process_progress_last_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_percent, 0)
        self.assertEqual(self.vendor_bill.current_approval_process_id.id, step_1.id)
        self.assertEqual(self.vendor_bill.completed_approval_process_id.id, False)

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.approval_process_progress_current_step, 0)
        self.assertEqual(self.vendor_bill.approval_process_progress_last_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_percent, 25)
        self.assertEqual(self.vendor_bill.current_approval_process_id.id, step_1.id)
        self.assertEqual(self.vendor_bill.completed_approval_process_id.id, False)

        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.approval_process_progress_current_step, 1)
        self.assertEqual(self.vendor_bill.approval_process_progress_last_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_percent, 50)
        self.assertEqual(self.vendor_bill.current_approval_process_id.id, step_2.id)
        self.assertEqual(self.vendor_bill.completed_approval_process_id.id, step_1.id)

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.approval_process_progress_current_step, 1)
        self.assertEqual(self.vendor_bill.approval_process_progress_last_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_percent, 75)
        self.assertEqual(self.vendor_bill.current_approval_process_id.id, step_2.id)
        self.assertEqual(self.vendor_bill.completed_approval_process_id.id, step_1.id)

        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.approval_process_progress_current_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_last_step, 2)
        self.assertEqual(self.vendor_bill.approval_process_progress_percent, 100)
        self.assertEqual(self.vendor_bill.current_approval_process_id.id, False)
        self.assertEqual(self.vendor_bill.completed_approval_process_id.id, step_2.id)

    def test_02_exceptions(self):
        journal = self.vendor_bill.journal_id

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_request_approval()
        self.assertIn(self.msg_1.format(ids=self.vendor_bill.id), e.exception.name)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_1.format(ids=self.vendor_bill.id), e.exception.name)

        self.vendor_bill.action_invoice_open()
        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_request_approval()
        self.assertIn(self.msg_1.format(ids=self.vendor_bill.id), e.exception.name)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_2.format(ids=self.vendor_bill.number), e.exception.name)

        self.vendor_bill = self.vendor_bill.copy()

        with self.assertRaises(ValidationError) as e:
            self.env.user.company_id.account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": -5,
                    },
                ),
            ]
        self.assertIn(self.msg_3, e.exception.name)

        self.env.user.company_id.account_approval_process_ids = [(5,)]
        with self.assertRaises(ValidationError) as e:
            self.env.user.company_id.account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": 0,
                        "validation_amount_to": -5,
                    },
                ),
            ]
        self.assertIn(self.msg_4, e.exception.name)
        self.env.user.company_id.account_approval_process_ids = [(5,)]
        with self.assertRaises(ValidationError) as e:
            self.env.user.company_id.account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": 10,
                        "validation_amount_to": 10,
                    },
                ),
            ]
        self.assertIn(self.msg_5, e.exception.name)

        with self.assertRaises(ValidationError) as e:
            journal.journal_account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": 0,
                        "validation_amount_to": 100,
                    },
                ),
            ]
        self.assertIn(
            self.msg_6.format(type=self.vendor_bill_type_str), e.exception.name
        )

        self.env.user.company_id.account_approval_process_ids = [(5,)]
        with self.assertRaises(ValidationError) as e:
            self.env.user.company_id.account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": "in_refund",
                        "name": "Test 0",
                        "validation_amount_from": 0,
                        "validation_amount_to": -1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": 0,
                        "validation_amount_to": 100,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test INVOICE_TYPES.get(journal.type)2",
                        "validation_amount_from": 100,
                        "validation_amount_to": 200,
                    },
                ),
            ]
        self.assertIn(
            self.msg_6.format(type=self.vendor_bill_type_str), e.exception.name
        )

        journal = self.vendor_bill.journal_id
        journal.overwrite_company_settings = True
        journal.journal_account_approval_process_ids = [(5,)]
        with self.assertRaises(ValidationError) as e:
            journal.journal_account_approval_process_ids = [
                (
                    0,
                    0,
                    {
                        "invoice_type": "out_refund",
                        "name": "Test 0",
                        "validation_amount_from": 0,
                        "validation_amount_to": -1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 1",
                        "validation_amount_from": 0,
                        "validation_amount_to": 100,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "invoice_type": self.invoice_type,
                        "name": "Test 2",
                        "validation_amount_from": 100,
                        "validation_amount_to": 200,
                    },
                ),
            ]
        self.assertIn(
            self.msg_6.format(type=self.vendor_bill_type_str), e.exception.name
        )

        def get_type_str(invoice_type):
            processes = self.env["account.approval.process"]
            return dict(processes.fields_get()["invoice_type"]["selection"]).get(
                invoice_type
            )

        types = "\n".join([get_type_str(t) for t in INVOICE_TYPES.get(journal.type)])
        self.assertIn(
            self.msg_7.format(journal=journal.name, types=types), e.exception.name
        )
        journal.overwrite_company_settings = False

        self.env.user.company_id.account_approval_process_ids = [(5,)]
        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                },
            ),
        ]

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_8.format(ids=self.vendor_bill.id), e.exception.name)

        self.env.user.company_id.account_approval_process_ids[0].user_ids = [
            (4, self.env.ref("base.user_root").id),
        ]

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)

    # def test_03_res_config_settings(self):
    #    settings = self.env['res.config.settings'].create({
    #        'account_approval_process_ids': [(0, 0, {
    #            'invoice_type': self.invoice_type,
    #            'name': "Test 1",
    #            'validation_amount_from': 0,
    #            'user_ids': [(4, self.env.ref('base.user_root').id)],
    #        }), (0, 0, {
    #            'invoice_type': self.invoice_type,
    #            'name': "Test 2",
    #            'validation_amount_from': 1000,
    #            'group_ids': [(4, self.env.ref('base.group_system').id)],
    #        }), ]
    #    })

    #    jaap_ids = settings.account_approval_process_ids
    #    self.assertEqual(len(jaap_ids), 2)
    #    self.assertEqual(self.vendor_bill.state, 'draft')
    #    self.assertTrue(self.vendor_bill.approval_needed)
    #    self.assertTrue(self.vendor_bill.approval_authorized)
    #    self.assertFalse(settings.has_invoices_for_reset)
    #
    #    self.vendor_bill.action_invoice_request_approval()
    #    self.assertTrue(settings.has_invoices_for_reset)

    #    settings.action_reset_journal_draft_invoices()
    #    self.assertFalse(settings.has_invoices_for_reset)

    def test_11_company_one_level_without_rights(self):
        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                },
            ),
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_8.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_requested)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_8.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

    def test_12_company_one_level_with_rights(self):
        self.assertFalse(self.env.user.company_id.has_invoices_for_reset)

        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "group_ids": [(4, self.env.ref("base.group_system").id)],
                },
            ),
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)
        self.assertFalse(self.env.user.company_id.has_invoices_for_reset)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(self.env.user.company_id.has_invoices_for_reset)

        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertTrue(self.env.user.company_id.has_invoices_for_reset)

        self.env.user.company_id.action_reset_journal_draft_invoices()
        self.assertFalse(self.env.user.company_id.has_invoices_for_reset)

        self.vendor_bill.action_invoice_approve()
        self.assertTrue(self.env.user.company_id.has_invoices_for_reset)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")
        self.assertFalse(self.env.user.company_id.has_invoices_for_reset)

    def test_13_company_two_levels_with_rights(self):
        template = self.env.ref(
            "account_approval_process.email_template_request_approval"
        )
        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "user_ids": [(4, self.env.ref("base.user_root").id)],
                },
            ),
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 2",
                    "validation_amount_from": 1000,
                    "email_template_id": template.id,
                    "group_ids": [(4, self.env.ref("base.group_system").id)],
                },
            ),
        ]

        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_request_approval()  # first step
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_approve()
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()  # second step
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_approve()
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertFalse(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")

    def test_21_journal_one_level_without_rights(self):
        journal = self.vendor_bill.journal_id
        journal.overwrite_company_settings = True
        journal.journal_account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                },
            ),
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_8.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_requested)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_approve()
        self.assertIn(self.msg_8.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

    def test_22_journal_one_level_with_rights(self):
        journal = self.vendor_bill.journal_id
        journal.overwrite_company_settings = True
        self.assertFalse(journal.has_invoices_for_reset)

        journal.journal_account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "group_ids": [(4, self.env.ref("base.group_system").id)],
                },
            ),
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)
        self.assertFalse(journal.has_invoices_for_reset)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(journal.has_invoices_for_reset)

        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertTrue(journal.has_invoices_for_reset)

        journal.action_reset_journal_draft_invoices()
        self.assertFalse(journal.has_invoices_for_reset)

        self.vendor_bill.action_invoice_approve()
        self.assertTrue(journal.has_invoices_for_reset)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")
        self.assertFalse(journal.has_invoices_for_reset)

    def test_23_journal_two_levels_with_rights(self):
        journal = self.vendor_bill.journal_id
        journal.overwrite_company_settings = True
        template = self.env.ref(
            "account_approval_process.email_template_request_approval"
        )
        journal.journal_account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "user_ids": [(4, self.env.ref("base.user_root").id)],
                },
            ),
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 2",
                    "validation_amount_from": 1000,
                    "email_template_id": template.id,
                    "group_ids": [(4, self.env.ref("base.group_system").id)],
                },
            ),
        ]

        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_request_approval()  # first step
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_approve()
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        with self.assertRaises(UserError) as e:
            self.vendor_bill.action_invoice_open()
        self.assertIn(self.msg_9.format(ids=self.vendor_bill.id), e.exception.name)
        self.assertEqual(self.vendor_bill.state, "draft")

        self.vendor_bill.action_invoice_request_approval()  # second step
        self.assertTrue(self.vendor_bill.approval_requested)
        self.assertTrue(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_approve()
        self.assertFalse(self.vendor_bill.approval_requested)
        self.assertFalse(self.vendor_bill.approval_needed)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")

    def test_24_journal_copy_company_settings(self):
        journal = self.vendor_bill.journal_id

        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "user_ids": [(4, self.env.ref("base.user_root").id)],
                },
            ),
            (
                0,
                0,
                {
                    "invoice_type": self.invoice_type,
                    "name": "Test 2",
                    "validation_amount_from": 1000,
                    "group_ids": [(4, self.env.ref("base.group_system").id)],
                },
            ),
        ]

        self.vendor_bill._compute_approval_process_ids()
        self.vendor_bill._compute_approval_process()
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)

        journal.overwrite_company_settings = True
        self.vendor_bill._compute_approval_process_ids()
        self.vendor_bill._compute_approval_process()
        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

        journal.action_copy_company_processes()
        self.vendor_bill._compute_approval_process_ids()
        self.vendor_bill._compute_approval_process()
        jaap_ids = journal.journal_account_approval_process_ids
        self.assertEqual(len(jaap_ids), 2)
        self.assertEqual(jaap_ids[0].journal_id.id, journal.id)
        self.assertEqual(jaap_ids[1].company_id.id, False)
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)
