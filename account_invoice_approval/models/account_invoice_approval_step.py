# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountInvoiceApprovalStep(models.Model):
    _name = 'account.invoice.approval.step'
    _order = 'sequence asc'

    approval_flow_id = fields.Many2one(
        comodel_name='account.invoice.approval.flow'
    )

    sequence = fields.Integer(
        default=0
    )

    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users',
        relation='invoice_approval_step_user_ids_rel'
    )

    override_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Allow Overrides By',
        relation='invoice_approval_step_override_user_ids_rel'
    )

    name = fields.Char(
        required=True,
        default='/'
    )

    _sql_constraints = [
        ('sequence_unique',
         'unique(approval_flow_id, sequence)',
         _('Sequence must be unique.')),
    ]
