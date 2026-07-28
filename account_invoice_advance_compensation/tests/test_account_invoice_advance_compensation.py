import runpy
from pathlib import Path
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestAccountInvoiceAdvanceCompensationUnified(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")

        cls.partner = cls._create_partner("Test Partner")
        cls.partner_2 = cls._create_partner("Other Partner")

        cls.currency_usd = cls._ref_optional("base.USD")

        cls.receivable = cls._get_core_account(
            [
                "account.demo_account_receivable",
                "l10n_generic_coa.demo_account_receivable",
                "account.data_account_receivable",
            ],
            account_type="asset_receivable",
            code="RCV100",
            name="Receivable",
            reconcile=True,
        )
        cls.payable = cls._get_core_account(
            [
                "account.demo_account_payable",
                "l10n_generic_coa.demo_account_payable",
                "account.data_account_payable",
            ],
            account_type="liability_payable",
            code="PAY100",
            name="Payable",
            reconcile=True,
        )
        cls.income = cls._get_core_account(
            [
                "account.demo_account_revenue",
                "l10n_generic_coa.demo_account_revenue",
                "account.data_account_revenue",
            ],
            account_type="income",
            code="INC100",
            name="Income",
        )
        cls.expense = cls._get_core_account(
            [
                "account.demo_account_expense",
                "l10n_generic_coa.demo_account_expense",
                "account.data_account_expense",
            ],
            account_type="expense",
            code="EXP100",
            name="Expense",
        )
        cls.prepayment = cls._get_core_account(
            [
                "account.demo_account_prepayments",
                "l10n_generic_coa.demo_account_prepayments",
            ],
            account_type="asset_prepayments",
            code="ADV100",
            name="Prepayments",
            reconcile=True,
        )
        cls.wrong_type_account = cls._get_core_account(
            [
                "account.demo_account_cash",
                "l10n_generic_coa.demo_account_cash",
                "account.demo_account_bank",
                "l10n_generic_coa.demo_account_bank",
            ],
            account_type="asset_current",
            code="CUR100",
            name="Current Asset",
            reconcile=True,
        )

        cls.product = cls._create_service_product()

        cls.advance_journal = cls._get_or_make_journal(
            ["account.miscellaneous_journal", "account.general_journal"],
            {
                "name": "Advance Journal",
                "code": "ADV",
                "type": "general",
                "is_advance_journal": True,
            },
        )
        cls.bank_journal = cls._get_or_make_journal(
            ["account.bank_journal", "account.demo_bank_journal"],
            {"name": "Bank Journal", "code": "BNK", "type": "bank"},
        )

        cls.advance_journal_usd = False

    @classmethod
    def _ref_optional(cls, xmlid):
        return cls.env["ir.model.data"]._xmlid_to_res_model_res_id(
            xmlid, raise_if_not_found=False
        )

    @classmethod
    def _create_partner(cls, name):
        with Form(cls.env["res.partner"]) as form:
            form.name = name
        return form.save()

    @classmethod
    def _create_service_product(cls):
        template = cls.env["product.template"].create(
            {
                "name": "Service",
                "type": "service",
                "categ_id": cls.env.ref("product.product_category_1").id,
                "property_account_income_id": cls.income.id,
                "property_account_expense_id": cls.expense.id,
            }
        )
        return template.product_variant_id

    @classmethod
    def _get_or_make_journal(cls, _xmlids, fallback_vals):
        vals = dict(fallback_vals, company_id=cls.company.id)
        return cls.env["account.journal"].create(vals)

    @classmethod
    def _get_core_account(cls, _xmlids, account_type, code, name, reconcile=False):
        return cls.env["account.account"].create(
            {
                "name": name,
                "code": code,
                "account_type": account_type,
                "reconcile": reconcile,
            }
        )

    def _create_move(self, move_type, partner, lines, date_field="invoice_date"):
        vals = {
            "move_type": move_type,
            "partner_id": partner.id,
            date_field: fields.Date.today(),
            "line_ids" if move_type == "entry" else "invoice_line_ids": lines,
        }
        move = (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            .create(vals)
        )
        return move

    def _post(self, move):
        move.action_post()
        move.invalidate_recordset()
        return move

    def _pay(self, move):
        with Form(
            self.env["account.payment.register"].with_context(
                active_model="account.move",
                active_ids=move.ids,
                active_id=move.id,
            )
        ) as form:
            form.payment_date = fields.Date.today()
            form.journal_id = self.bank_journal
        wizard = form.save()
        wizard._create_payments()
        move.invalidate_recordset()
        self.assertEqual(move.payment_state, "paid")
        return move

    def _invoice(self, move_type, amount, partner=None, account=None):
        partner = partner or self.partner
        account = account or (
            self.income if move_type == "out_invoice" else self.expense
        )
        lines = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "price_unit": amount,
                    "account_id": account.id,
                },
            )
        ]
        return self._create_move(move_type, partner, lines, date_field="invoice_date")

    def _invoice_posted(self, move_type, amount):
        return self._post(self._invoice(move_type, amount))

    def _invoice_paid(self, move_type, amount):
        return self._pay(self._invoice_posted(move_type, amount))

    def _advance_invoice(self, move_type, amount, partner=None):
        partner = partner or self.partner
        lines = [
            (
                0,
                0,
                {
                    "name": "Advance",
                    "quantity": 1,
                    "price_unit": amount,
                    "account_id": self.prepayment.id,
                },
            )
        ]
        return self._create_move(move_type, partner, lines, date_field="invoice_date")

    def _advance_invoice_posted(self, move_type, amount, partner=None):
        move = self._advance_invoice(move_type, amount, partner=partner)
        return self._post(move)

    def _advance_invoice_paid(self, move_type, amount, partner=None):
        move = self._advance_invoice_posted(move_type, amount, partner=partner)
        return self._pay(move)

    def _partner_line(self, move):
        return move.line_ids.filtered(
            lambda line: line.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )

    def _prepayment_lines(self, move):
        return move.line_ids.filtered(lambda line: line.account_id == self.prepayment)

    def _wizard(self, invoice, invoice_line, advance_line, amount, journal=None):
        journal = journal or self.advance_journal
        wizard = (
            self.env["account.invoice.advance.compensation.wizard"]
            .with_context(
                active_model="account.move",
                active_ids=[invoice.id],
                active_id=invoice.id,
                default_move_id=invoice.id,
                default_move_type=invoice.move_type,
            )
            .create(
                {
                    "invoice_line_id": invoice_line.id,
                    "advance_line_id": advance_line.id,
                    "journal_id": journal.id,
                    "amount": amount,
                    "date": fields.Date.today(),
                }
            )
        )
        wizard.invalidate_recordset()
        return wizard

    def _wizard_write(self, wizard, vals):
        wizard.write(vals)
        wizard.invalidate_recordset()
        return wizard

    def _compute_adv_flag(self, invoice):
        invoice.invalidate_recordset()
        _ = invoice.advance_invoice
        return invoice.advance_invoice

    def test_journal_field_and_flag(self):
        self.assertIn("is_advance_journal", self.env["account.journal"]._fields)
        self.assertTrue(self.advance_journal.is_advance_journal)

    def test_move_compute_domain_and_open_action(self):
        invoice = self._invoice_posted("out_invoice", 1000)
        self.assertFalse(self._compute_adv_flag(invoice))
        with self.assertRaises(ValidationError):
            invoice.action_open_advance_compensation()

        advance = self._advance_invoice_paid("out_invoice", 500)
        self.assertTrue(self._prepayment_lines(advance))
        self.assertTrue(self._compute_adv_flag(invoice))

        domain = invoice._get_advance_domain(invoice.partner_id, "asset_prepayments")
        self.assertTrue(self.env["account.move.line"].search(domain, limit=1))

        action = invoice.action_open_advance_compensation()
        self.assertEqual(
            action["res_model"], "account.invoice.advance.compensation.wizard"
        )
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_move_id"], invoice.id)
        self.assertEqual(action["context"]["default_move_type"], invoice.move_type)

        invoice_no_partner = invoice.copy()
        invoice_no_partner.write({"partner_id": False})
        with self.assertRaises(ValidationError):
            invoice_no_partner.action_open_advance_compensation()

        entry = self._create_move(
            "entry",
            self.partner,
            [
                (
                    0,
                    0,
                    {
                        "name": "x",
                        "account_id": self.receivable.id,
                        "debit": 10.0,
                        "credit": 0.0,
                        "partner_id": self.partner.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "y",
                        "account_id": self.receivable.id,
                        "debit": 0.0,
                        "credit": 10.0,
                        "partner_id": self.partner.id,
                    },
                ),
            ],
            date_field="date",
        )
        self._post(entry)
        with self.assertRaises(ValidationError):
            entry.action_open_advance_compensation()

    def test_move_line_name_get_and_validations(self):
        advance = self._advance_invoice_paid("out_invoice", 120)
        advance_line = self._prepayment_lines(advance)
        self.assertTrue(advance_line)

        res_default = advance_line.name_get()
        self.assertTrue(res_default and isinstance(res_default[0][1], str))

        res_adv = advance_line.with_context(advance_id_name_get=True).name_get()
        self.assertTrue(res_adv and isinstance(res_adv[0][1], str))
        res_adv_direct = advance_line._get_advance_display_name()
        self.assertTrue(res_adv_direct and isinstance(res_adv_direct[0][1], str))

        invoice = self._invoice_posted("out_invoice", 200)
        inv_partner_line = self._partner_line(invoice)
        inv_partner_line.write(
            {"name": "Partner Line", "date_maturity": fields.Date.today()}
        )

        res_inv = inv_partner_line.with_context(line_id_name_get=True).name_get()
        self.assertTrue(res_inv and isinstance(res_inv[0][1], str))
        res_inv_direct = inv_partner_line._get_invoice_line_display_name()
        self.assertTrue(res_inv_direct and isinstance(res_inv_direct[0][1], str))

        advance_line._validate_advance_line()

        advance_line.write({"account_id": self.wrong_type_account.id})
        with self.assertRaises(ValidationError):
            advance_line._validate_advance_line()
        advance_line.write({"account_id": self.prepayment.id})

        self.prepayment.write({"reconcile": False})
        with self.assertRaises(ValidationError):
            advance_line._validate_advance_line()
        self.prepayment.write({"reconcile": True})

        advance_line.remove_move_reconcile()
        advance_line.write({"amount_residual": 0})
        with self.assertRaises(ValidationError):
            advance_line._validate_advance_line()

        inv_partner_line._validate_invoice_line()
        with self.assertRaises(ValidationError):
            advance_line._validate_invoice_line()

        inv_partner_line.write({"amount_residual": 0})
        with self.assertRaises(ValidationError):
            inv_partner_line._validate_invoice_line()

        entry = self._create_move(
            "entry",
            self.partner,
            [
                (
                    0,
                    0,
                    {
                        "name": "z1",
                        "account_id": self.receivable.id,
                        "debit": 1.0,
                        "credit": 0.0,
                        "partner_id": self.partner.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "z2",
                        "account_id": self.receivable.id,
                        "debit": 0.0,
                        "credit": 1.0,
                        "partner_id": self.partner.id,
                    },
                ),
            ],
            date_field="date",
        )
        entry_line = entry.line_ids[:1]
        with self.assertRaises(ValidationError):
            entry_line._validate_invoice_line()

    def test_wizard_fields_onchange_available_lines_currency(self):
        advance = self._advance_invoice_paid("out_invoice", 300)
        invoice = self._invoice_posted("out_invoice", 500)
        self.assertTrue(self._compute_adv_flag(invoice))

        inv_line = self._partner_line(invoice)
        adv_line = self._prepayment_lines(advance)

        wiz = self._wizard(
            invoice, inv_line, adv_line, 10, journal=self.advance_journal
        )

        wiz._compute_currency()
        self.assertEqual(wiz.currency_id, self.advance_journal.company_id.currency_id)

        wiz._compute_available_advance_lines()
        self.assertTrue(wiz.available_advance_line_ids)

        wiz._compute_advance_balance()
        self.assertAlmostEqual(
            wiz.advance_balance, abs(adv_line.amount_residual), places=2
        )

        wiz = self._wizard_write(wiz, {"amount": 0})
        wiz._onchange_invoice_line_id()
        wiz = self._wizard_write(
            wiz, {"invoice_line_id": inv_line.id, "advance_line_id": adv_line.id}
        )
        wiz._onchange_invoice_line_id()
        self.assertGreater(wiz.amount, 0)

        bill_adv = self._advance_invoice_paid("in_invoice", 100)
        bill = self._invoice_posted("in_invoice", 200)
        bill_line = self._partner_line(bill)
        bill_adv_line = self._prepayment_lines(bill_adv)
        bill_wiz = self._wizard(bill, bill_line, bill_adv_line, 10)
        available = bill_wiz._get_available_advance_lines()
        self.assertTrue(all(line.amount_residual > 0 for line in available))

    def test_wizard_validate_prepare_and_confirm(self):
        advance = self._advance_invoice_paid("out_invoice", 500)
        invoice = self._invoice_posted("out_invoice", 1000)
        self.assertTrue(self._compute_adv_flag(invoice))

        inv_line = self._partner_line(invoice)
        adv_line = self._prepayment_lines(advance)

        wiz = self._wizard(invoice, inv_line, adv_line, 300)

        wiz = self._wizard_write(wiz, {"amount": 0})
        with self.assertRaises(ValidationError):
            wiz._validate_compensation()

        wiz = self._wizard_write(
            wiz,
            {
                "advance_line_id": adv_line.id,
                "amount": abs(inv_line.amount_residual) + 1,
            },
        )
        with self.assertRaises(ValidationError):
            wiz._validate_compensation()

        wiz = self._wizard_write(wiz, {"amount": abs(adv_line.amount_residual) + 1})
        with self.assertRaises(ValidationError):
            wiz._validate_compensation()

        wiz = self._wizard_write(wiz, {"amount": 300})

        vals = wiz._prepare_move_vals()
        self.assertEqual(vals["move_type"], "entry")
        self.assertEqual(vals["journal_id"], self.advance_journal.id)
        self.assertEqual(len(vals["line_ids"]), 2)

        comp_line = wiz._prepare_compensation_line()
        adv_comp_line = wiz._prepare_advance_line()
        self.assertEqual(comp_line["credit"], 300)
        self.assertEqual(adv_comp_line["debit"], 300)

        move_unposted = wiz._create_compensation_move()
        with self.assertRaises(ValidationError):
            wiz._process_reconciliation(move_unposted)

        posted_move = wiz._create_compensation_move()
        posted_move.action_post()

        def _raise_on_reconcile(*args, **kwargs):
            raise Exception("boom")

        with patch(
            "odoo.addons.account.models.account_move_line.AccountMoveLine.reconcile",
            new=_raise_on_reconcile,
        ):
            with self.assertRaises(ValidationError):
                wiz._process_reconciliation(posted_move)

        wiz = self._wizard(invoice, inv_line, adv_line, 300)
        action = wiz.action_confirm_compensation()
        self.assertEqual(action["res_model"], "account.move")

        move = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(move.state, "posted")
        self.assertEqual(len(move.line_ids), 2)

        invoice.button_draft()
        wiz = self._wizard(invoice, inv_line, adv_line, 30)
        with self.assertRaises(ValidationError):
            wiz.action_confirm_compensation()

    def test_wizard_validation_branches_and_manifest(self):
        manifest_path = Path(__file__).resolve().parents[1] / "__manifest__.py"
        manifest_exec = runpy.run_path(str(manifest_path))
        self.assertEqual(manifest_exec["__file__"], str(manifest_path))

        self._invoice_paid("out_invoice", 50)
        invoice = self._invoice_posted("out_invoice", 300)
        inv_line = self._partner_line(invoice)
        advance = self._advance_invoice_paid("out_invoice", 150)
        adv_line = self._prepayment_lines(advance)
        wiz = self._wizard(invoice, inv_line, adv_line, 100)

        empty_wiz = self.env["account.invoice.advance.compensation.wizard"].new({})
        self.assertFalse(empty_wiz._get_available_advance_lines())
        with self.assertRaises(ValidationError):
            empty_wiz._validate_compensation()
        empty_wiz_amount = self.env["account.invoice.advance.compensation.wizard"].new(
            {"amount": 10}
        )
        with self.assertRaises(ValidationError):
            empty_wiz_amount._validate_compensation()

        wiz_no_line = self.env["account.invoice.advance.compensation.wizard"].new(
            {
                "move_id": invoice.id,
                "advance_line_id": adv_line.id,
                "journal_id": self.advance_journal.id,
                "amount": 10,
                "date": fields.Date.today(),
            }
        )
        with self.assertRaises(ValidationError):
            wiz_no_line._validate_compensation()

        wiz_no_adv = self.env["account.invoice.advance.compensation.wizard"].new(
            {
                "move_id": invoice.id,
                "invoice_line_id": inv_line.id,
                "journal_id": self.advance_journal.id,
                "amount": 10,
                "date": fields.Date.today(),
            }
        )
        with self.assertRaises(ValidationError):
            wiz_no_adv._validate_compensation()

        wiz_no_journal = self.env["account.invoice.advance.compensation.wizard"].new(
            {
                "move_id": invoice.id,
                "invoice_line_id": inv_line.id,
                "advance_line_id": adv_line.id,
                "amount": 10,
                "date": fields.Date.today(),
            }
        )
        with self.assertRaises(ValidationError):
            wiz_no_journal._validate_compensation()

        wiz_bad_journal = self._wizard(
            invoice,
            inv_line,
            adv_line,
            10,
            journal=self.bank_journal,
        )
        with self.assertRaises(ValidationError):
            wiz_bad_journal._validate_compensation()

        invoice_other = self._invoice_posted("out_invoice", 200)
        inv_line_other = self._partner_line(invoice_other)
        wiz_wrong_invoice_line = self._wizard(invoice, inv_line_other, adv_line, 10)
        with self.assertRaises(ValidationError):
            wiz_wrong_invoice_line._validate_compensation()

        adv_other = self._advance_invoice_paid(
            "out_invoice", 80, partner=self.partner_2
        )
        adv_line_other = self._prepayment_lines(adv_other)
        wiz_wrong_partner = self._wizard(invoice, inv_line, adv_line_other, 10)
        with self.assertRaises(ValidationError):
            wiz_wrong_partner._validate_compensation()

        invoice.button_draft()
        with self.assertRaises(ValidationError):
            wiz._validate_compensation()
        invoice.action_post()

        entry = self._create_move(
            "entry",
            self.partner,
            [
                (
                    0,
                    0,
                    {
                        "name": "a",
                        "account_id": self.receivable.id,
                        "debit": 5.0,
                        "credit": 0.0,
                        "partner_id": self.partner.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "b",
                        "account_id": self.receivable.id,
                        "debit": 0.0,
                        "credit": 5.0,
                        "partner_id": self.partner.id,
                    },
                ),
            ],
            date_field="date",
        )
        self._post(entry)
        wiz_on_entry = self.env["account.invoice.advance.compensation.wizard"].new(
            {
                "move_id": entry.id,
                "invoice_line_id": inv_line.id,
                "advance_line_id": adv_line.id,
                "journal_id": self.advance_journal.id,
                "amount": 10,
                "date": fields.Date.today(),
            }
        )
        with self.assertRaises(ValidationError):
            wiz_on_entry._validate_compensation()

        wrong_move = self._post(
            self._create_move(
                "entry",
                self.partner,
                [
                    (
                        0,
                        0,
                        {
                            "name": "x1",
                            "account_id": self.receivable.id,
                            "debit": 10.0,
                            "credit": 0.0,
                            "partner_id": self.partner.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "x2",
                            "account_id": self.receivable.id,
                            "debit": 0.0,
                            "credit": 10.0,
                            "partner_id": self.partner.id,
                        },
                    ),
                ],
                date_field="date",
            )
        )
        with self.assertRaises(ValidationError):
            wiz._process_reconciliation(wrong_move)
