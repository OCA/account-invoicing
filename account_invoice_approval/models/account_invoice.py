# Copyright 2019 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(
        selection_add=[
            ('to_review', 'Waiting for Review'),
            ('approved', 'Approved'),
            ('refused', 'Refused')
        ], track_visibility='always'
    )

    approval_flow_id = fields.Many2one(
        string='Flow',
        comodel_name='account.invoice.approval.flow'
    )

    approval_step_id = fields.Many2one(
        string='Current Step',
        comodel_name='account.invoice.approval.step'
    )

    approval_step_user_ids = fields.Many2many(
        string='Waiting for',
        comodel_name='res.users'
    )

    user_awaiting_review = fields.Boolean(
        compute='_compute_user_awaiting_review'
    )

    requesting_user_id = fields.Many2one(
        string='Requestor',
        comodel_name='res.users'
    )

    user_override_allowed = fields.Boolean(
        compute='_compute_user_override_allowed'
    )

    override_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Allowed overrides by',
        relation='account_invoice_override_user_ids_rel',
        related='approval_step_id.override_user_ids'
    )

    approved_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Approved by',
        relation='account_invoice_approved_user_ids_rel',
    )

    @api.multi
    @api.depends('approval_step_user_ids')
    def _compute_user_awaiting_review(self):
        for invoice in self:
            invoice.user_awaiting_review = self.env.user in invoice.approval_step_user_ids

    @api.multi
    @api.depends('approval_step_id', 'approval_step_id.override_user_ids')
    def _compute_user_override_allowed(self):
        for invoice in self:
            invoice.user_override_allowed = self.env.user in invoice.approval_step_id.override_user_ids

    @api.multi
    def _get_approval_flow(self):
        self.ensure_one()
        flows = self.env['account.invoice.approval.flow'].search([], order='sequence asc')
        for flow in flows:
            domain = flow.domain and safe_eval(flow.domain) or []
            if self.search([('id', '=', self.id)] + domain):
                return flow
        return False

    @api.multi
    def submit_for_review(self):
        self.ensure_one()

        # Check invoice
        if not self.journal_id.sequence_id:
            raise UserError(
                _('Please define sequence on the journal related to this invoice.')
            )
        if not self.invoice_line_ids:
            raise UserError(
                _('Please create some invoice lines.')
            )

        self.approval_flow_id = self._get_approval_flow()

        # If there is no approval flow it is automatically approved
        state = self.approval_flow_id and self.approval_flow_id.step_ids and 'to_review' or 'approved'

        if state == 'to_review':
            first_step = self._get_next_step()
            self.requesting_user_id = self.env.user
            self._go_to_step(first_step)

        self.state = state

    @api.multi
    def _get_next_step(self):
        self.ensure_one()
        if self.approval_step_id:
            current_sequence = self.approval_step_id.sequence
            next_steps = self.approval_flow_id.step_ids.filtered(lambda s: s.sequence > current_sequence)
            if next_steps:
                step = next_steps[0]
            else:
                step = False
        else:
            step = self.approval_flow_id.step_ids[0]
        return step

    @api.multi
    def _go_to_step(self, step, mail_template_xml_id=False, subtype=False):
        self.ensure_one()
        self.approval_step_id = step
        self.approval_step_user_ids = self.approval_step_id.user_ids
        self.message_subscribe_users(self.approval_step_user_ids.ids)

        # Send mails
        mail_template_xml_id = mail_template_xml_id or 'account_invoice_approval.mail_template_invoice_review_request'
        subtype = subtype or 'account_invoice_approval.subtype_state_to_review'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template = self.env.ref(mail_template_xml_id)
        body = self.env['mail.template'].with_context(
            base_url=base_url).render_template(
            template.body_html, 'account.invoice', self.id)
        self.message_post(
            subject=template.subject,
            body=body,
            subtype=subtype,
            message_type='email',
            partner_ids=[(6, 0, [p.id for p in self.approval_step_user_ids.mapped('partner_id')])]
        )

    @api.multi
    def approve(self):
        self.ensure_one()
        if not self.user_awaiting_review:
            raise UserError(
                _('You are not allowed to approve or already have reviewed this invoice.')
            )

        self.approval_step_user_ids = [(3, self.env.user.id, 0)]
        self.approved_user_ids = [(4, self.env.user.id, 0)]

        if not self.approval_step_user_ids:
            next_step = self._get_next_step()
            if next_step:
                self._go_to_step(next_step)
            else:
                self.state = 'approved'
                self.approval_step_id = False

    @api.multi
    def refuse(self):
        self.ensure_one()
        if not self.user_awaiting_review:
            raise UserError(
                _('You are not allowed to refused or already have reviewed this invoice.')
            )

        self.state = 'refused'
        self.approval_step_id = False
        self.approval_step_user_ids = [(5, 0, 0)]
        self.approved_user_ids = [(5, 0, 0)]

        # Send mail
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template = self.env.ref('account_invoice_approval.mail_template_invoice_refused')
        body = self.env['mail.template'].with_context(
            base_url=base_url).render_template(
            template.body_html, 'account.invoice', self.id)
        self.message_post(
            subject=template.subject,
            body=body,
            subtype='account_invoice_approval.subtype_state_refused',
            message_type='email',
            partner_ids=[(6, 0, [self.requesting_user_id.id])]
        )

    @api.multi
    def action_invoice_open(self):
        # Check approved
        for invoice in self:
            if invoice.state != 'approved':
                raise ValidationError(
                    _('This invoice has not been approved yet.')
                )

        # Change state so super works.
        self.state = 'draft'
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def refused_to_draft(self):
        if self.filtered(lambda inv: inv.state != 'refused'):
            raise UserError(_("Invoice must be refused in order to reset it to draft."))

        for invoice in self:
            invoice.state = 'draft'

    @api.multi
    def override_approval(self):
        self.ensure_one()
        if self.env.user not in self.approval_step_id.override_user_ids:
            raise UserError(_("You're not allowed to override this approval step."))

        self.approved_user_ids = [(4, self.env.user.id, 0)]
        next_step = self._get_next_step()
        if next_step:
            self._go_to_step(next_step)
        else:
            self.state = 'approved'
            self.approval_step_id = False
