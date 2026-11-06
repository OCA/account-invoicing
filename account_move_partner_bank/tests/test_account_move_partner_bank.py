# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestAccountPartnerBank(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up a dedicated company, so that the tests do not depend on the data
        # (bank accounts in particular) of the companies already in the database.
        cls.company = cls.env["res.company"].create({"name": "Test Company"})
        cls.env.user.write(
            {
                "company_ids": [Command.link(cls.company.id)],
                "company_id": cls.company.id,
            }
        )
        cls.env["account.journal"].create(
            [
                {
                    "name": "Test Sales Journal",
                    "code": "TSAJ",
                    "type": "sale",
                    "company_id": cls.company.id,
                },
                {
                    "name": "Test Purchase Journal",
                    "code": "TPUJ",
                    "type": "purchase",
                    "company_id": cls.company.id,
                },
            ]
        )
        cls.bank_account_1 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "11110000",
                "partner_id": cls.company.partner_id.id,
                "sequence": 10,
            }
        )
        cls.bank_account_2 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "22220000",
                "partner_id": cls.company.partner_id.id,
                "sequence": 20,
            }
        )
        cls.bank_account_3 = cls.env["res.partner.bank"].create(
            {
                "acc_number": "33330000",
                "partner_id": cls.company.partner_id.id,
                "sequence": 30,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.account_move_model = cls.env.ref("account.model_account_move")
        cls.source = cls.env["bank.account.source"].create(
            {
                "company_id": cls.company.id,
                "sequence": 20,
                "source_model_id": cls.account_move_model.id,
                "bank_field_path": "commercial_partner_id.bank_account_id",
            }
        )

    def create_contact_source(self):
        """Let the contact's own bank account take precedence."""
        return self.env["bank.account.source"].create(
            {
                "company_id": self.company.id,
                "sequence": 10,
                "source_model_id": self.account_move_model.id,
                "bank_field_path": "partner_id.bank_account_id",
            }
        )

    def create_invoice(self, partner, move_type="out_invoice"):
        return self.env["account.move"].create(
            {"move_type": move_type, "partner_id": partner.id}
        )

    def create_other_company_source(self):
        """A source of a company the test user has no access to."""
        other_company = self.env["res.company"].create({"name": "Test Company 2"})
        return self.env["bank.account.source"].create(
            {
                "company_id": other_company.id,
                "source_model_id": self.account_move_model.id,
                "bank_field_path": "partner_id.bank_account_id",
            }
        )

    def test_bank_field_path_constraint(self):
        # A random string
        with self.assertRaises(ValidationError):
            self.source.write({"bank_field_path": "test"})
        # Not a real field
        with self.assertRaises(ValidationError):
            self.source.write({"bank_field_path": "partner_id.bank_account"})
        # A real field but not many2one to res.partner.bank
        with self.assertRaises(ValidationError):
            self.source.write({"bank_field_path": "partner_id.country_id"})
        # A path that holds no field name
        with self.assertRaises(ValidationError):
            self.source.write({"bank_field_path": " "})
        with self.assertRaises(ValidationError):
            self.source.write({"bank_field_path": "."})
        # The path is validated on create as well
        with self.assertRaises(ValidationError):
            self.env["bank.account.source"].create(
                {
                    "company_id": self.company.id,
                    "source_model_id": self.account_move_model.id,
                    "bank_field_path": "partner_id.country_id",
                }
            )
        # An abstract model cannot serve as a source model
        with self.assertRaises(ValidationError):
            self.env["bank.account.source"].create(
                {
                    "company_id": self.company.id,
                    "source_model_id": self.env.ref(
                        "account_move_partner_bank.model_bank_account_mixin"
                    ).id,
                    "bank_field_path": "bank_account_id",
                }
            )
        self.source.write({"bank_field_path": "partner_id.bank_account_id"})

    def test_bank_field_path_normalization(self):
        # Whitespace is stripped from the stored path, as it is passed as is to
        # attrgetter
        self.source.write({"bank_field_path": " partner_id . bank_account_id "})
        self.assertEqual(self.source.bank_field_path, "partner_id.bank_account_id")
        source = self.env["bank.account.source"].create(
            {
                "company_id": self.company.id,
                "sequence": 30,
                "source_model_id": self.account_move_model.id,
                "bank_field_path": " commercial_partner_id . bank_account_id ",
            }
        )
        self.assertEqual(
            source.bank_field_path, "commercial_partner_id.bank_account_id"
        )
        # The normalized path resolves at runtime
        self.partner.bank_account_id = self.bank_account_2
        move = self.create_invoice(self.partner)
        self.assertEqual(move.partner_bank_id, self.bank_account_2)

    def test_account_move_partner_bank(self):
        # Odoo's default proposes bank_account_1 (lower sequence)
        move = self.create_invoice(self.partner)
        self.assertEqual(move.partner_bank_id, self.bank_account_1)
        # Assigning bank_account_id to partner supersedes Odoo's default
        self.partner.bank_account_id = self.bank_account_2
        move = self.create_invoice(self.partner)
        self.assertEqual(move.partner_bank_id, self.bank_account_2)

    def test_vendor_bill_keeps_core_behavior(self):
        # Outbound moves are left to the standard behavior: the bank account of the
        # vendor applies, and the sources are not resolved
        vendor_bank = self.env["res.partner.bank"].create(
            {"acc_number": "44440000", "partner_id": self.partner.id}
        )
        self.partner.bank_account_id = self.bank_account_2
        move = self.create_invoice(self.partner, move_type="in_invoice")
        self.assertEqual(move.partner_bank_id, vendor_bank)

    def test_bank_account_from_commercial_entity(self):
        # The bank account of the commercial entity applies to its contacts, without
        # being copied to them
        self.partner.bank_account_id = self.bank_account_2
        contact = self.env["res.partner"].create(
            {"name": "Test Contact", "parent_id": self.partner.id}
        )
        self.assertFalse(contact.bank_account_id)
        move = self.create_invoice(contact)
        self.assertEqual(move.partner_bank_id, self.bank_account_2)
        # An update on the commercial entity applies to the contacts as well
        self.partner.bank_account_id = self.bank_account_1
        move = self.create_invoice(contact)
        self.assertEqual(move.partner_bank_id, self.bank_account_1)

    def test_bank_account_contact_override(self):
        # A contact can collect on its own bank account (e.g. a branch), while the
        # other contacts of the company keep using the one of the commercial entity
        self.create_contact_source()
        self.partner.bank_account_id = self.bank_account_2
        branch, other_contact = self.env["res.partner"].create(
            [
                {
                    "name": "Test Branch",
                    "parent_id": self.partner.id,
                    "bank_account_id": self.bank_account_1.id,
                },
                {"name": "Test Contact", "parent_id": self.partner.id},
            ]
        )
        move = self.create_invoice(branch)
        self.assertEqual(move.partner_bank_id, self.bank_account_1)
        move = self.create_invoice(other_contact)
        self.assertEqual(move.partner_bank_id, self.bank_account_2)
        # An update on the commercial entity does not overwrite the branch
        self.partner.bank_account_id = self.bank_account_3
        self.assertEqual(branch.bank_account_id, self.bank_account_1)
        move = self.create_invoice(other_contact)
        self.assertEqual(move.partner_bank_id, self.bank_account_3)

    def test_bank_account_child_company(self):
        # A child company is its own commercial entity, so it keeps its bank account
        self.partner.bank_account_id = self.bank_account_2
        child_company = self.env["res.partner"].create(
            {
                "name": "Test Child Company",
                "parent_id": self.partner.id,
                "is_company": True,
                "bank_account_id": self.bank_account_1.id,
            }
        )
        move = self.create_invoice(child_company)
        self.assertEqual(move.partner_bank_id, self.bank_account_1)

    def test_bank_account_company_dependent(self):
        # The bank account is resolved in the company of the record, not in the one
        # of the environment
        other_company = self.env["res.company"].create({"name": "Test Company 2"})
        self.partner.bank_account_id = self.bank_account_2
        move = self.create_invoice(self.partner)
        bank = self.source.get_bank_for_record(move.with_company(other_company))
        self.assertEqual(bank, self.bank_account_2)

    def test_source_multi_company_rule(self):
        # The tests above run as superuser, which bypasses the record rules: check
        # the multi-company rule with a plain internal user
        other_source = self.create_other_company_source()
        user = new_test_user(
            self.env, login="test_source_user", company_id=self.company.id
        )
        sources = self.env["bank.account.source"].with_user(user).search([])
        self.assertIn(self.source, sources)
        self.assertNotIn(other_source, sources)
        # The source becomes visible once its company is allowed
        user.write({"company_ids": [Command.link(other_source.company_id.id)]})
        sources = (
            self.env["bank.account.source"]
            .with_user(user)
            .with_context(
                allowed_company_ids=(self.company + other_source.company_id).ids
            )
            .search([])
        )
        self.assertIn(other_source, sources)
        # Only settings users may configure the sources
        with self.assertRaises(AccessError):
            self.source.with_user(user).write({"sequence": 40})

    def test_bank_assigned_for_internal_user(self):
        # The stored compute resolves the sources on behalf of the invoicing user,
        # so it must not be blocked by the access rights on bank.account.source
        self.create_other_company_source()
        user = new_test_user(
            self.env,
            login="test_invoicing_user",
            groups="base.group_user,account.group_account_invoice",
            company_id=self.company.id,
        )
        self.partner.bank_account_id = self.bank_account_2
        move = (
            self.env["account.move"]
            .with_user(user)
            .create({"move_type": "out_invoice", "partner_id": self.partner.id})
        )
        self.assertEqual(move.partner_bank_id, self.bank_account_2)

    def test_bank_account_of_other_company_skipped(self):
        # A source that resolves to a bank account of another company is skipped, as
        # such an account cannot be set on the move (check_company)
        other_company = self.env["res.company"].create({"name": "Test Company 2"})
        other_partner = self.env["res.partner"].create(
            {"name": "Test Partner 2", "company_id": other_company.id}
        )
        other_bank = self.env["res.partner.bank"].create(
            {"acc_number": "55550000", "partner_id": other_partner.id}
        )
        self.assertEqual(other_bank.company_id, other_company)
        self.create_contact_source()
        self.partner.bank_account_id = self.bank_account_2
        contact = self.env["res.partner"].create(
            {
                "name": "Test Contact",
                "parent_id": self.partner.id,
                "bank_account_id": other_bank.id,
            }
        )
        move = self.create_invoice(contact)
        self.assertEqual(move.partner_bank_id, self.bank_account_2)
