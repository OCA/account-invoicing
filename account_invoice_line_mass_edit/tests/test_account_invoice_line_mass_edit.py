# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from lxml import etree

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceLineMassEdit(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mass_edit_action = cls.env.ref(
            "account_invoice_line_mass_edit.action_mass_edit_invoice_line"
        )
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Mass Edit Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Mass Edit Test Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {"display_type": "line_section", "name": "Test Section"}
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_b.id,
                            "quantity": 2.0,
                            "price_unit": 50.0,
                        }
                    ),
                    Command.create({"display_type": "line_note", "name": "Test Note"}),
                ],
            }
        )
        cls.product_lines = cls.invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        cls.section_and_note_lines = cls.invoice.invoice_line_ids.filtered(
            lambda line: line.display_type in ("line_section", "line_note")
        )
        cls.section_line = cls.invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        cls.note_line = cls.invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_note"
        )

    def _add_mass_edit_line(self, field_name):
        """Add a field to the invoice lines mass edit action."""
        self.env["ir.actions.server.mass.edit.line"].create(
            {
                "server_action_id": self.mass_edit_action.id,
                "field_id": self.env.ref(
                    f"account.field_account_move_line__{field_name}"
                ).id,
            }
        )

    def _mass_edit(self, server_action, records, vals):
        """Run the mass editing wizard of the given action and apply the values."""
        action = server_action.with_context(
            active_model=records._name,
            active_ids=records.ids,
        ).run()
        return (
            self.env[action["res_model"]]
            .with_context(**literal_eval(action["context"]))
            .create(vals)
        )

    def test_mass_edit_analytic_distribution(self):
        """The analytic distribution is set on the product lines."""
        analytic_distribution = {str(self.analytic_account.id): 100.0}
        self._mass_edit(
            self.mass_edit_action,
            self.invoice.invoice_line_ids,
            {
                "selection__analytic_distribution": "set",
                "analytic_distribution": analytic_distribution,
            },
        )
        self.assertEqual(
            self.product_lines.mapped("analytic_distribution"),
            [analytic_distribution] * 2,
        )
        self.assertFalse(
            any(self.section_and_note_lines.mapped("analytic_distribution"))
        )

    def test_mass_edit_ignores_sections_and_notes(self):
        """Sections and notes are selected for information, but never updated."""
        self._add_mass_edit_line("name")
        self._mass_edit(
            self.mass_edit_action,
            self.invoice.invoice_line_ids,
            {"selection__name": "set", "name": "Renamed line"},
        )
        self.assertEqual(set(self.product_lines.mapped("name")), {"Renamed line"})
        self.assertEqual(self.section_line.name, "Test Section")
        self.assertEqual(self.note_line.name, "Test Note")

    def test_mass_edit_other_model(self):
        """Mass editing still works on models other than account.move.line."""
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        server_action = self.env["ir.actions.server"].create(
            {
                "name": "Mass Edit Test Partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "state": "mass_edit",
            }
        )
        self.env["ir.actions.server.mass.edit.line"].create(
            {
                "server_action_id": server_action.id,
                "field_id": self.env.ref("base.field_res_partner__name").id,
            }
        )
        self._mass_edit(
            server_action, partner, {"selection__name": "set", "name": "New name"}
        )
        self.assertEqual(partner.name, "New name")

    def test_technical_fields_are_hidden_in_wizard(self):
        wizard = self.env["mass.editing.wizard"]
        arch = etree.fromstring('<group name="group_field_list"/>')
        for line in self.mass_edit_action.mass_edit_line_ids:
            wizard._insert_field_in_arch(line, line.field_id, arch)
        for field_name in ("company_id", "analytic_precision"):
            label = arch.find(f"./label[@for='selection__{field_name}']")
            self.assertEqual(label.get("invisible"), "1")
            selection_field = arch.find(f".//field[@name='selection__{field_name}']")
            self.assertEqual(selection_field.get("invisible"), "1")
            value_field = arch.find(f".//div/field[@name='{field_name}']")
            self.assertEqual(value_field.get("invisible"), "1")
        analytic_field = arch.find(".//div/field[@name='analytic_distribution']")
        self.assertNotEqual(analytic_field.get("invisible"), "1")
        self.assertEqual(analytic_field.get("widget"), "analytic_distribution")
