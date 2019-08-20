# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceApprovalFlow(models.Model):
    _name = 'account.invoice.approval.flow'
    _inherit = ['mail.thread']

    sequence = fields.Integer(
        default=10,
        track_visibility='always'
    )

    active = fields.Boolean(
        default=True,
        track_visibility='always'
    )

    domain = fields.Text()

    step_ids = fields.One2many(
        string='Steps',
        comodel_name='account.invoice.approval.step',
        inverse_name='approval_flow_id',
        track_visibility='always'
    )
