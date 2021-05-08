# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sequence_option = fields.Boolean(
        compute="_compute_name",
        default=False,
        copy=False,
        store=True,
        index=True,
    )

    @api.depends("posted_before", "state", "journal_id", "date")
    def _compute_name(self):
        # On post, get the sequence option
        for rec in self.filtered(
            lambda l: l.name in (False, "/") and l.state == "posted"
        ):
            sequence = self.env["sequence.option"].get_sequence(rec)
            if sequence:
                rec.name = sequence.next_by_id(sequence_date=rec.date)
                rec.sequence_option = True

        # Call super()
        super()._compute_name()

        # On draft, odoo may still suggest the 1st new number too, remove it.
        for rec in self.filtered(
            lambda l: l.name not in (False, "/") and l.state == "draft"
        ):
            sequence = self.env["sequence.option"].get_sequence(rec)
            if sequence:
                rec.name = "/"

    # Bypass constrains if sequence is defined
    def _constrains_date_sequence(self):
        for record in self:
            sequence = self.env["sequence.option"].get_sequence(record)
            if not sequence:
                record.super()._constrains_date_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        (where_string, param) = super()._get_last_sequence_domain(relaxed=relaxed)
        where_string += " AND coalesce(sequence_option, false) = false "
        return where_string, param
