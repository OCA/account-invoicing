# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MassEditingWizard(models.TransientModel):
    _inherit = "mass.editing.wizard"

    @api.model
    def _insert_field_in_arch(self, line, field, main_xml_group):
        field_element = super()._insert_field_in_arch(line, field, main_xml_group)
        # The analytic_distribution widget needs the company_id and
        # analytic_precision fields to work, but the user must not see them
        # in the wizard (see the CONFIGURE section of the module description)
        technical_fields_to_hide = ("company_id", "analytic_precision")
        if field.name in technical_fields_to_hide:
            field_element.set("invisible", "1")
            label_node = main_xml_group.find(f"./label[@for='selection__{field.name}']")
            if label_node is not None:
                label_node.set("invisible", "1")
            selection_node = main_xml_group.find(
                f".//field[@name='selection__{field.name}']"
            )
            if selection_node is not None:
                selection_node.set("invisible", "1")
        return field_element

    def _exec_write(self, server_action, vals):
        # Sections and notes are displayed in the invoice lines list in order to
        # give the same vision as in the invoice, but they must never be updated
        # by the wizard (no analytic distribution on a section or a note, ...)
        if server_action.model_id.model != "account.move.line":
            return super()._exec_write(server_action, vals)
        active_ids = self.env.context.get("active_ids", [])
        records = self.env["account.move.line"].browse(active_ids)
        to_remove_ids = records.filtered(
            lambda line: line.display_type in ("line_section", "line_note")
        ).ids
        new_active_ids = list(set(active_ids) - set(to_remove_ids))
        return super(
            MassEditingWizard, self.with_context(active_ids=new_active_ids)
        )._exec_write(server_action, vals)
