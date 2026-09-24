# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from operator import attrgetter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BankAccountSource(models.Model):
    _name = "bank.account.source"
    _description = "Bank Account Source"
    _order = "sequence, id"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    source_model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        help="The model from which the bank field path is resolved.",
    )
    bank_field_path = fields.Char(
        required=True,
        help="Field path to res.partner.bank (e.g. partner_id.bank_account_id).",
    )

    @api.constrains("source_model_id", "bank_field_path")
    def _check_bank_field_path(self):
        for rec in self:
            model = self.env.get(rec.source_model_id.model)
            if model is None or model._abstract or model._transient:
                raise ValidationError(
                    _("Invalid source model: %s") % rec.source_model_id.model
                )
            parts = [p for p in (rec.bank_field_path or "").split(".") if p]
            if not parts:
                raise ValidationError(
                    _("Invalid bank field path: %s") % rec.bank_field_path
                )
            for attr in parts[:-1]:
                field = model._fields.get(attr)
                if not field or field.type != "many2one":
                    raise ValidationError(
                        _("Invalid bank field path: %s") % rec.bank_field_path
                    )
                model = self.env[field.comodel_name]
            last = model._fields.get(parts[-1])
            if (
                not last
                or last.type != "many2one"
                or last.comodel_name != "res.partner.bank"
            ):
                raise ValidationError(
                    _("Invalid path (last field must reference res.partner.bank): %s")
                    % rec.bank_field_path
                )

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._normalize_vals(vals) for vals in vals_list])

    def write(self, vals):
        return super().write(self._normalize_vals(vals))

    @api.model
    def _normalize_vals(self, vals):
        """Store the field path free of stray whitespace, as it is passed as is to
        attrgetter in get_bank_for_record."""
        if not vals.get("bank_field_path"):
            return vals
        path = ".".join(
            p.strip() for p in vals["bank_field_path"].split(".") if p.strip()
        )
        if not path:
            # Leave the value untouched so that the constraint rejects it.
            return vals
        return {**vals, "bank_field_path": path}

    def get_bank_for_record(self, record):
        """Find bank from sources for the given record."""
        record.ensure_one()
        company = record.company_id if "company_id" in record._fields else False
        if company:
            # The bank account fields in the path may be company-dependent (as on
            # res.partner), so resolve them in the company of the record.
            record = record.with_company(company)
        # Sort explicitly, as _order is only applied when the recordset is read from
        # the database, while sequence is the priority mechanism here.
        sources = self.sorted("sequence").filtered(
            lambda s: s.source_model_id.model == record._name
        )
        for source in sources:
            bank = attrgetter(source.bank_field_path)(record) or False
            if not bank:
                continue
            if company and bank.company_id and bank.company_id != company:
                # A bank account of another company cannot be assigned (the target
                # fields are typically check_company).
                continue
            return bank
        return False
