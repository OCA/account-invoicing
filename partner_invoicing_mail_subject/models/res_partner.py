# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_email_subject = fields.Char(
        string="Individual invoice mail subject",
        company_dependent=True,
        help="""
    Use placeholders like "{{ object.name }}" (result → invoice number) or
    "{{ object.partner_id.name }}" (result → customer name). You can combine them with
    free text.

    Example: Document: {{ object.name }} from {{ object.invoice_date }} - Thank you
        → will result in: Document: INV/2026/04 from 2026-04-25 - Thank you

    Only direct field paths are supported (object.field or object.relation.field).
    No functions or expressions (e.g. {{ object.partner_id.name | upper }}).
    """,
    )

    @api.constrains("invoice_email_subject")
    def _check_invoice_email_subject(self):
        for partner in self:
            template = partner.invoice_email_subject or ""
            if not template:
                continue

            matches = re.finditer(
                r"(\{\{\s*object\.([a-zA-Z0-9_\.]+)\s*\}\})", template
            )
            invalid = []
            for m in matches:
                full_expr = m.group(1)
                field_path = m.group(2)

                if not self._field_exists(self.env["account.move"], field_path):
                    invalid.append(full_expr)

            if invalid:
                msg = self.env._("Invalid invoice email subject field(s):\n%s")
                fields = "\n".join(f"- {expr}" for expr in invalid)
                raise ValidationError(msg % fields)

    @api.model
    def _field_exists(self, model, field_path):
        current = model
        parts = field_path.split(".")
        for i, part in enumerate(parts):
            field = current._fields.get(part)
            if not field:
                return False

            if i < len(parts) - 1:
                if not field.relational or not field.comodel_name:
                    return False

                current = self.env[field.comodel_name]

        return True
