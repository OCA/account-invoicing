# Copyright (C) 2024-Today - KMEE (<http://www.kmee.com.br>).
# @author Diego Paradeda <diego.paradeda@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

JOURNAL_TYPE_MAP = {
    ("outgoing", "customer"): ["sale"],
    ("outgoing", "supplier"): ["purchase"],
    ("outgoing", "transit"): ["sale", "purchase"],
    ("incoming", "supplier"): ["purchase"],
    ("incoming", "customer"): ["sale"],
    ("incoming", "transit"): ["purchase", "sale"],
}

INVOICE_TYPE_MAP = {
    # Picking Type Code | Local Origin Usage | Local Dest Usage
    ("outgoing", "internal", "customer"): "out_invoice",
    ("incoming", "customer", "internal"): "out_refund",
    ("incoming", "supplier", "internal"): "in_invoice",
    ("outgoing", "internal", "supplier"): "in_refund",
    ("incoming", "transit", "internal"): "in_invoice",
    ("outgoing", "transit", "supplier"): "in_refund",
    ("outgoing", "transit", "customer"): "out_invoice",
}


class AccountMoveMatchPicking(models.TransientModel):
    _name = "account.move.match.picking"
    _description = "Account Move Match Picking"

    account_move_id = fields.Many2one(
        comodel_name="account.move",
        readonly=True,
    )

    # Invoice lines match status fields
    count_lines = fields.Integer(compute="_compute_line_counts")
    count_lines_matched = fields.Integer(compute="_compute_matched")
    unmatched_invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Unmatched lines",
        relation="account_move_match_unmatched_invoice_line_ids",
        column1="match_wizard_id",
        column2="account_move_id",
        readonly=True,
        compute="_compute_unmatched",
        help="These account.move.lines have no match with a transfer.",
    )
    partial_match_invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Partial match lines",
        relation="account_move_match_partial_match_invoice_line_ids",
        column1="match_wizard_id",
        column2="account_move_id",
        readonly=True,
        compute="_compute_partial",
        help="These account.move.lines have a match with a transfer but the quantity"
        " match is partial.",
    )
    full_match_invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Full match lines",
        relation="account_move_match_full_match_invoice_line_ids",
        column1="match_wizard_id",
        column2="account_move_id",
        readonly=True,
        compute="_compute_matched",
        help="These account.move.lines have a complete match with one or more stock"
        " transfer",
    )

    # Picking selection fields
    stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Stock Pickings",
        relation="account_move_match_pickings",
        column1="match_wizard_id",
        column2="picking_id",
    )
    new_stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="New Stock Pickings",
        relation="account_move_match_new_pickings",
        column1="match_wizard_id",
        column2="picking_id",
    )
    candidate_stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Candidate stock pickings",
        relation="account_move_match_canditate_pickings",
        column1="match_wizard_id",
        column2="picking_id",
    )
    candidate_stock_picking_count = fields.Integer(
        string="Candidate Stock pickings candidates",
    )
    count_lines_matching = fields.Integer(compute="_compute_matching")
    matching_invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Matching lines (full)",
        relation="account_move_match_matching_invoice_line_ids",
        column1="match_wizard_id",
        column2="account_move_id",
        readonly=True,
        compute="_compute_matching",
        help="These account.move.lines will be fully matched once the current set of"
        " stock pickings is confirmed.",
    )
    matching_progress = fields.Float(
        compute="_compute_matching_progress",
        group_operator="avg",
        string="Progress",
    )

    # Wizard actions
    can_action_exact_match = fields.Boolean(
        string="Can exact match",
        default=1,
    )
    can_action_create_all = fields.Boolean(
        string="Can create all",
        default=1,
    )
    can_action_match_create = fields.Boolean(
        string="Can match and create",
        default=1,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["account_move_id"] = self._context.get("active_id")
        return res

    # Invoice lines status methods
    @api.onchange("account_move_id")
    def _compute_line_counts(self):
        aml = self.account_move_id.invoice_line_ids
        self.count_lines = len(aml)

    @api.onchange("account_move_id")
    def _compute_unmatched(self):
        aml = self.account_move_id.invoice_line_ids
        fully_unmatched = aml.filtered(lambda line: not line.move_line_ids)
        self.unmatched_invoice_line_ids = fully_unmatched

    def _compute_partial(self):
        # TODO: later
        self.partial_match_invoice_line_ids = False

    @api.onchange("account_move_id")
    def _compute_matched(self):
        """
        Determine whether invoice lines are fully reconciled with the quantities in
        the corresponding stock moves
        """
        for line in self.account_move_id.invoice_line_ids:
            sml = line.mapped("move_line_ids")
            transfer_quantity = sum(sml.mapped("quantity_done"))

            # Case exact match
            # TODO: consider checking product_uom_qty too
            if transfer_quantity == line.quantity:
                self.full_match_invoice_line_ids += line

        self.count_lines_matched = len(self.full_match_invoice_line_ids)

    # Picking status methods
    @api.onchange("account_move_id")
    def get_stock_picking_ids(self):
        aml = self.account_move_id.invoice_line_ids
        self.stock_picking_ids = aml.mapped("move_line_ids.picking_id")
        self.new_stock_picking_ids = self.stock_picking_ids
        self.get_candidate_picking_ids()

    def get_candidate_picking_ids(self):
        partner_id = self.account_move_id.partner_id
        candidate_ids = self.env["stock.picking"].search(
            [
                ("partner_id", "=", partner_id.id),
                ("state", "=", "assigned"),
            ]
        )
        # Keep only pickings that have at least one product in common
        product_ids = self.account_move_id.invoice_line_ids.mapped("product_id")
        candidate_ids = candidate_ids.filtered(
            lambda pick: pick.mapped("product_id") in product_ids
        )
        # Remove already matched pickings
        candidate_ids = [
            id for id in candidate_ids.ids if id not in self.stock_picking_ids.ids
        ]
        self.candidate_stock_picking_ids = candidate_ids
        self.candidate_stock_picking_count = len(candidate_ids)

    @api.onchange("new_stock_picking_ids")
    def _compute_matching(self):
        # TODO: merge with action_exact_match
        """
        Determine whether invoice lines will be fully matched once the current set of
        stock pickings is confirmed.
        """
        self.matching_invoice_line_ids = False
        sml = self.new_stock_picking_ids.move_lines

        for line in self.account_move_id.invoice_line_ids:
            # Propose a random match for line
            same_prod_id = sml.filtered(lambda move: move.product_id == line.product_id)
            # TODO: consider checking product_uom_qty too
            same_qty = same_prod_id.filtered(
                lambda sml: sml.quantity_done == line.quantity
            )

            # Case exact match
            if same_qty:
                match_move = same_qty[0]
                sml -= match_move
                self.matching_invoice_line_ids += line

        self.count_lines_matching = len(self.matching_invoice_line_ids)

    @api.onchange("matching_invoice_line_ids", "count_lines_matching")
    def _compute_matching_progress(self):
        if not self.count_lines:
            self.matching_progress = 0
        else:
            self.matching_progress = 100 * self.count_lines_matching / self.count_lines

    # Wizard actions methods
    def action_exact_match(self):
        # TODO: merge with _compute_matching
        self.matching_invoice_line_ids = False
        sml = self.new_stock_picking_ids.move_lines

        for line in self.account_move_id.invoice_line_ids:
            # Propose a random match for line
            same_prod_id = sml.filtered(lambda move: move.product_id == line.product_id)
            # TODO: consider checking product_uom_qty too
            same_qty = same_prod_id.filtered(
                lambda sml: sml.quantity_done == line.quantity
            )

            # Case exact match
            if same_qty:
                match_move = same_qty[0]
                sml -= match_move
                line.move_line_ids += match_move
                self.matching_invoice_line_ids += line

        self.count_lines_matching = len(self.matching_invoice_line_ids)

        if self.matching_invoice_line_ids != self.account_move_id.invoice_line_ids:
            raise UserError(_("All invoice lines must have a match"))
        if sml:
            raise UserError(_("All selected pickings must be fully matched"))

    def action_create_all(self):
        self.account_move_id.action_generate_pickings_from_invoices()

    def action_match_create(self):
        pass

    def action_unmatch_all(self):
        aml = self.account_move_id.invoice_line_ids
        for line in aml:
            line.move_line_ids = False
