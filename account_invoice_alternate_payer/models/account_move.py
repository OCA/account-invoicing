# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    alternate_payer_id = fields.Many2one(
        "res.partner",
        string="Alternate Payer",
        help="If set, this will be the partner that we expect to pay or to "
        "be paid by. If not set, the payor is by default the "
        "commercial",
    )

    @api.depends("alternate_payer_id")
    def _compute_bank_partner_id(self):
        super_moves = self.filtered(
            lambda r: not r.alternate_payer_id or not r.is_outbound()
        )
        for move in self - super_moves:
            if move.is_outbound() and move.alternate_payer_id:
                move.bank_partner_id = move.alternate_payer_id
        return super(
            AccountMove,
            super_moves,
        )._compute_bank_partner_id()

    @api.onchange("alternate_payer_id")
    def _onchange_alternate_payer_id(self):
        return self._onchange_partner_id()

    @contextmanager
    def _sync_dynamic_line(
        self,
        existing_key_fname,
        needed_vals_fname,
        needed_dirty_fname,
        line_type,
        container,
    ):
        records_with_alternate_player = container.get("records").filtered(
            lambda x: x.alternate_payer_id
        )
        with super()._sync_dynamic_line(
            existing_key_fname,
            needed_vals_fname,
            needed_dirty_fname,
            line_type,
            container,
        ):
            if line_type == "payment_term" and records_with_alternate_player:
                for invoice in container.get("records").filtered(
                    lambda x: x.alternate_payer_id
                ):
                    payment_term_lines = invoice.line_ids.filtered(
                        lambda x: x.display_type == "payment_term"
                    )
                    payment_term_lines.write(
                        {
                            "partner_id": invoice.alternate_payer_id.id,
                        }
                    )
            yield

    def _compute_payments_widget_to_reconcile_info(self):
        super_moves = self.filtered(lambda r: not r.alternate_payer_id)
        for move in self - super_moves:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False
            if (
                move.state != "posted"
                or move.payment_state not in ("not_paid", "partial")
                or not move.is_invoice(include_receipts=True)
            ):
                continue

            # https://github.com/odoo/odoo/blob/f82f768729d897fa54b04789f4e0637ed1bb27f4/addons/account/models/account_move.py#L1298
            pay_term_lines = move.line_ids.filtered(
                lambda line: line.account_id.account_type
                in ("asset_receivable", "liability_payable")
            )

            # https://github.com/odoo/odoo/blob/f82f768729d897fa54b04789f4e0637ed1bb27f4/addons/account/models/account_move.py#L1301-L1307
            domain = [
                ("account_id", "in", pay_term_lines.account_id.ids),
                "|",
                ("parent_state", "=", "posted"),
                "&",
                ("parent_state", "=", "draft"),
                ("partner_id", "=", move.alternate_payer_id.id),
                ("reconciled", "=", False),
                "|",
                ("amount_residual", "!=", 0.0),
                ("amount_residual_currency", "!=", 0.0),
            ]

            # https://github.com/odoo/odoo/blob/f82f768729d897fa54b04789f4e0637ed1bb27f4/addons/account/models/account_move.py#L1309
            payments_widget_vals = {
                "outstanding": True,
                "content": [],
                "move_id": move.id,
            }

            if move.is_inbound():
                domain.append(("balance", "<", 0.0))
                payments_widget_vals["title"] = _("Outstanding credits")
            else:
                domain.append(("balance", ">", 0.0))
                payments_widget_vals["title"] = _("Outstanding debits")

            for line in self.env["account.move.line"].search(domain):
                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = line.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )
                if move.currency_id.is_zero(amount):
                    continue

                # https://github.com/odoo/odoo/blob/f82f768729d897fa54b04789f4e0637ed1bb27f4/addons/account/models/account_move.py#L1335-L1343
                payments_widget_vals["content"].append(
                    {
                        "journal_name": line.ref or line.move_id.name,
                        "amount": amount,
                        "currency_id": move.currency_id.id,
                        "id": line.id,
                        "move_id": line.move_id.id,
                        "date": fields.Date.to_string(line.date),
                        "account_payment_id": line.payment_id.id,
                    }
                )

            if not payments_widget_vals["content"]:
                continue

            move.invoice_outstanding_credits_debits_widget = payments_widget_vals
            move.invoice_has_outstanding = True
        return super(
            AccountMove, super_moves
        )._compute_payments_widget_to_reconcile_info()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, values):
        # CHECK ME: this change to commercial partner when find difference between main partner # noqa
        # https://github.com/odoo/odoo/blob/f82f7687/addons/account/models/account_move.py#L4914
        if "partner_id" in values and len(values.keys()) == 1:
            lines_to_skip = self.filtered(
                lambda x: x.move_id.alternate_payer_id
                and x.display_type == "payment_term"
                and x.partner_id == x.move_id.alternate_payer_id
            )
            return super(AccountMoveLine, self - lines_to_skip).write(values)
        return super().write(values)
