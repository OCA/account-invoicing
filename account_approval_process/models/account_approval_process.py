# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _


class AccountApprovalProcess(models.Model):
    _name = "account.approval.process"
    _description = "Account approval process"
    _order = "company_id,sequence,id"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
    )
    invoice_type = fields.Selection(
        selection=[
            ("out_invoice", "Customer Invoice"),
            ("in_invoice", "Vendor Bill"),
            ("out_refund", "Customer Credit Note"),
            ("in_refund", "Vendor Credit Note"),
        ],
        required=True,
        index=True,
    )

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        help="Utility field to express amount currency",
        readonly=True,
        store=True,
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        required=True,
    )

    name = fields.Char(
        required=True,
    )

    validation_amount_from = fields.Monetary(
        string="Amount (from)",
        currency_field="company_currency_id",
        default=0,
        required=True,
        help="Begin of the validation net total amount",
    )

    validation_amount_to = fields.Monetary(
        string="Amount (to)",
        currency_field="company_currency_id",
        default=-1,
        help="End of the validation net total amount",
    )

    email_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        ondelete="SET NULL",
        domain=[
            ("model", "=", "account.invoice"),
        ],
        help="Mail template which is used for the notification",
    )

    group_ids = fields.Many2many(
        comodel_name="res.groups",
        string="Allowed Groups",
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Allowed Users",
    )

    approvers = fields.Char(
        compute="_compute_approvers",
        readonly=True,
    )

    active = fields.Boolean(
        default=True,
    )

    @api.constrains("validation_amount_to", "validation_amount_from")
    def _check_validation_amount(self):
        msg = []

        if any(c.validation_amount_from < 0 for c in self):
            msg.append(_("The field 'Amount (from)' must be positive."))

        if any(
            False
            if c.validation_amount_to > 0 or c.validation_amount_to == -1.0
            else True
            for c in self
        ):
            msg.append(
                _("The field 'Amount (to)' must be positive or -1 for unlimited.")
            )

        elif any(
            True
            if c.validation_amount_to != -1.0
            and c.validation_amount_from >= c.validation_amount_to
            else False
            for c in self
        ):
            msg.append(
                _(
                    "The field 'Amount (to)' must be greater than the field 'Amount "
                    "(from)'."
                )
            )

        if msg:
            raise exceptions.ValidationError("\n".join(msg))

    def _compute_approvers(self):
        for i in self:
            users = i.get_users_with_access_rights()
            i.approvers = ",".join([str(u.partner_id.id) for u in users])

    def get_users_with_access_rights(self):
        users = self.user_ids
        for group in self.group_ids:
            users |= group.users
        return users

    def has_current_user_access_rights(self):
        user_group_ids = set(self.env.user.groups_id.ids)
        allowed_group_ids = set(self.group_ids.ids)
        allowed_user_ids = set(self.user_ids.ids)
        has_group = bool(allowed_group_ids.intersection(user_group_ids))
        return self.env.user.id in allowed_user_ids or has_group
