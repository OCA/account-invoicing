# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_pdf_filename = fields.Char(
        string="Invoice PDF Filename",
        company_dependent=True,
        help=(
            "Partner-specific invoice PDF filename template.\n"
            "You can use Jinja-like placeholders which are rendered dynamically "
            "when generating the filename:\n\n"
            "  {{ object.name }}             → Invoice reference\n"
            "  {{ object.partner_id.name }}   → Partner name\n"
            "  {{ object.invoice_date }}      → Invoice date\n\n"
            "  Example:\n"
            "  Invoice_{{ object.name }}_{{ object.partner_id.name }}\n\n"
            "If left empty, the default report filename is used."
        ),
    )

    @api.constrains("invoice_pdf_filename")
    def _check_invoice_pdf_filename(self):
        for partner in self:
            template = partner.invoice_pdf_filename or ""
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
                allowed_msg = self.env._(
                    "Allowed format is based on account.move fields, e.g.:\n"
                    "- {{ object.name }}\n"
                    "- {{ object.partner_id.name }}\n"
                    "- {{ object.invoice_date }}"
                )
                msg = self.env._(
                    "Invalid invoice PDF filename fields:\n%(fields)s\n\n%(allowed)s",
                    fields="\n".join(f"- {i}" for i in invalid),
                    allowed=allowed_msg,
                )
                raise ValidationError(msg)

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
