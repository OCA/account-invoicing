# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import List

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import first


class AccountMove(models.Model):
    _inherit = "account.move"

    validation_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Validation user",
        index=True,
        compute="_compute_validation_user_id",
        store=True,
        readonly=False,
    )

    date_assignation = fields.Date(
        help="Date of last assignation to this user",
        compute="_compute_date_assignation",
        store=True,
        readonly=False,
    )

    validation_state = fields.Selection(
        [
            ("wait_approval", "Waiting approval"),
            ("accepted", "Accepted"),
            ("refused", "Refused"),
            ("locked", "Waiting/Blocked"),
        ],
        help="Validation state of the invoice/refund",
        readonly=True,
        # Empty default value for invoice not-concerned
        default="",
        index=True,
        tracking=True,
        store=True,
        compute="_compute_validation_state",
    )

    pending_date = fields.Date(
        readonly=True,
        help="Date (not included) to ignore document when sending reminders"
        " to validate purchase invoice/refund",
    )

    note = fields.Char(
        help="Reason of the last modification of the state",
    )

    can_edit_validation_user = fields.Boolean(
        help="Technical field: true if user can edit validation user",
        compute="_compute_can_edit_validation_user",
    )

    @api.depends("move_type")
    def _compute_validation_user_id(self):

        for rec in self:
            # if validation user is not set and move typ is in concerned types
            if (
                rec.move_type in rec.get_concerned_types()
                and not rec.validation_user_id
            ):
                rec.validation_user_id = rec.company_id.validation_user_id

    @api.depends_context("uid")
    def _compute_can_edit_validation_user(self):
        self.can_edit_validation_user = self.env.user.has_group(
            "account.group_account_manager"
        )

    @api.depends("validation_user_id")
    def _compute_validation_state(self) -> None:
        self.filtered(lambda rec: rec.validation_user_id).update(
            {"validation_state": "wait_approval"}
        )

    @api.depends("validation_user_id")
    def _compute_date_assignation(self) -> None:
        self.filtered(lambda rec: rec.validation_user_id).update(
            {"date_assignation": fields.Date.today()}
        )

    def action_open_invoice(self) -> str:
        """
        Action to open related invoice
        :return: dict (action)
        """
        return self.get_formview_action()

    @api.model
    def get_concerned_types(self) -> List[str]:
        """
        Get invoice types concerned by this module.
        # We should use get_purchase_types() but for backward compatibility,
        do not delete it now (instead of define them everywhere)
        :return: list of str
        """
        return self.get_purchase_types()

    def validation_state_wait_approval(self) -> None:
        """
        Update the validation state to wait_approval
        :return: dict
        """
        validation_state = "wait_approval"
        values = {
            "validation_state": validation_state,
            "pending_date": False,
        }
        self._update_validation_state(values, validation_state)
        return {}

    def action_accept_state(self) -> None:
        """
        action called by the button to change state to accept
        """
        if not self.invoice_date:
            raise ValidationError(_("Please provide an invoice date!"))
        if not self.partner_id:
            raise ValidationError(_("Please provide the supplier of the invoice!"))
        self.validation_state_accepted(
            self.partner_id,
            self.ref,
            self.invoice_date,
        )

    def validation_state_accepted(
        self,
        supplier_id: int,
        reference: str,
        date_invoice: str,
    ) -> dict:
        """
        Update the validation state to accepted
        :param supplier_id: int
        :param date_invoice: str
        :return: dict
        """
        validation_state = "accepted"
        line = first(self.invoice_line_ids)
        values = {
            "invoice_line_ids": [
                (
                    1,
                    line.id,
                    {
                        "company_id": line.company_id.id,
                    },
                ),
            ],
            "partner_id": supplier_id,
            "validation_state": validation_state,
            "invoice_date": date_invoice,
            "pending_date": False,
            "ref": reference,
        }
        self._check_before_update_validation_state(validation_state)
        self.write(values)
        return {}

    def action_refuse_state(self):
        """
        action calling the wizard account_move_note
        """
        formid = self.env.ref(
            "account_invoice_validation.account_move_note_form_view"
        ).id
        context = self.env.context.copy()
        context.update({"movingToState": "refuse"})
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move.note",
            "view_id": formid,
            "target": "new",
            "context": context,
        }

    def action_refuse_state_continue(self, note: str) -> dict:
        """
        Update the validation state to refused with a message (reason)
        :param note: str
        :return: dict
        """

        validation_state = "refused"
        values = {
            "validation_state": validation_state,
            "pending_date": False,
        }
        self._update_validation_state(values, validation_state)
        for rec in self:
            rec.message_post(body=note)
        return {}

    def _check_before_update_validation_state(self, validation_state: str) -> bool:
        """
        Do some check before update the validation_state
        :param validation_state: str
        :return: bool
        """
        types = self.get_concerned_types()
        invoices = self.filtered(lambda i: i.move_type not in types)
        if invoices:
            details = "\n- ".join(invoices.mapped("display_name"))
            message = (
                _("These documents are not supplier " "invoice/refund:\n- %s") % details
            )
            raise ValidationError(message)
        return True

    def _update_validation_state(self, values: dict, validation_state: str) -> bool:
        """
        Update the validation state with the given value
        We can put some check before the write if necessary
        :param validation_state: str
        :return: bool
        """
        self._check_before_update_validation_state(validation_state)
        return self.write(values)

    def action_block_state(self):
        """
        action calling the wizard account_move_note from block button
        """
        formid = self.env.ref(
            "account_invoice_validation.account_move_note_form_view"
        ).id
        context = self.env.context.copy()
        context.update({"movingToState": "blocked"})
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move.note",
            "view_id": formid,
            "target": "new",
            "context": context,
        }

    def action_block_state_continue(self, note: str, pending_date: str) -> dict:
        """
        Update the validation state to locked
        :param pending_date: str (date)
        :param note: str
        :return: dict
        """
        self._check_pending_date(pending_date)
        if not note:
            message = _("Please specify a note!")
            raise UserError(message)
        validation_state = "locked"
        values = {
            "validation_state": validation_state,
            "pending_date": pending_date,
        }
        self._update_validation_state(values, validation_state)
        for rec in self:
            rec.message_post(body=note)
        return {}

    def _check_pending_date(self, pending_date: str) -> bool:
        """
        If the validity of the given pending date
        :param pending_date: str (date)
        :return: bool
        """
        if not pending_date:
            message = _("Please set a pending date!")
            raise UserError(message)
        real_date = fields.Date.from_string(pending_date)
        if real_date <= fields.Date.from_string(fields.Date.today()):
            message = _("Please set a pending date greater than today!")
            raise UserError(message)
        return True

    def action_assign(self) -> dict:
        """
        action calling the wizard account_move_note from assign button
        """
        formid = self.env.ref(
            "account_invoice_validation.account_move_note_form_view"
        ).id
        context = self.env.context.copy()
        context.update({"movingToState": "assign"})
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move.note",
            "view_id": formid,
            "target": "new",
            "context": context,
        }

    def action_assign_continue(self, note: str) -> str:
        for rec in self:
            if not rec.validation_user_id:
                message = _("Please define a User to re-assign the invoice/refund")
                raise UserError(message)

            if not rec.partner_id:
                raise ValidationError(_("Please provide the supplier of the invoice!"))
            for r in rec:
                r.message_post(body=note)
            rec.redirect_approval()

    def redirect_approval(self):
        """
        The user_id will be
        follower of current invoices.
        :param note: str
        """
        user = self.env["res.users"].browse(self.validation_user_id.id)
        # Send email to the user
        partner_ids = user.partner_id.ids

        # Add it to follower
        self.message_subscribe(partner_ids=user.mapped("partner_id").ids)
        for rec in self:
            values = {
                "validation_user_id": self.validation_user_id.id,
                "pending_date": False,
                "date_assignation": fields.Date.today(),
                "partner_id": self.partner_id,
            }
            rec._check_before_update_validation_state("assign")
            rec.write(values)
        # Send the email after because the validation_user_id is not
        # already updated

        self.message_post_with_view(
            "account_invoice_validation.message_validation_user_assigned",
            composition_mode="mass_mail",
            partner_ids=[(4, pid) for pid in partner_ids],
            auto_delete=True,
            auto_delete_message=True,
            parent_id=False,  # override accidental context defaults
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return {}

    @api.model
    def notify_validation_process_waiting(self):
        """
        Cron function to execute as Admin (to avoid multi-company issues)
        Steps:
        - Get invoices (with validation state 'wait_approval');
        - To have less emails, group invoices by users
        - Launch notifications
        :return:
        """

        types = self.get_concerned_types()
        domain = [
            ("move_type", "in", types),
            ("validation_state", "=", "wait_approval"),
        ]
        invoices = self.search(domain)
        users = invoices.mapped("validation_user_id")
        template = self.env.ref(
            "account_invoice_validation.mail_template_invoice_assign_late"
        )
        for user in users:
            current_invoices = invoices.filtered(
                lambda i, u=user: i.validation_user_id == u
            )
            template.with_context(
                reminder_account_invoice_ids=current_invoices.ids
            ).send_mail(user.id)
