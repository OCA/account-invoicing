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

    state = fields.Selection(
        [("main", "Main"), ("select", "Select")],
        string="State",
        default="main",
    )

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
    new_match_line_ids = fields.One2many(
        comodel_name="account.move.match.picking.line",
        string="New Match Lines",
        inverse_name="new_match_wizard_id",
        ondelete="cascade",
    )
    candidate_stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Candidate stock pickings",
        relation="account_move_match_canditate_pickings",
        column1="match_wizard_id",
        column2="picking_id",
    )
    candidate_match_line_ids = fields.One2many(
        comodel_name="account.move.match.picking.line",
        string="Candidate Match Lines",
        inverse_name="candidate_match_wizard_id",
        ondelete="cascade",
    )
    candidate_stock_picking_count = fields.Integer(
        string="Candidate Stock pickings candidates",
    )
    count_lines_matching = fields.Integer(
        string="Matching Lines",
    )
    matching_invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Matching lines (full)",
        relation="account_move_match_matching_invoice_line_ids",
        column1="match_wizard_id",
        column2="account_move_id",
        readonly=True,
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
            if transfer_quantity == line.quantity:
                self.full_match_invoice_line_ids += line

        self.count_lines_matched = len(self.full_match_invoice_line_ids)

    # Picking status methods
    @api.onchange("account_move_id")
    def get_stock_picking_ids(self):
        pickings_to_add = self.env.context.get("default_new_stock_picking_ids", [])

        aml = self.account_move_id.invoice_line_ids
        self.stock_picking_ids = aml.mapped("move_line_ids.picking_id")

        pickings = self.stock_picking_ids.ids + pickings_to_add

        self.new_stock_picking_ids = pickings

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

    def _get_transfer_qty(self, stock_moves):
        qty = 0
        for move in stock_moves:
            qty += move.quantity_done if move.quantity_done else move.product_uom_qty
        return qty

    def _set_matching_invoice_lines(self, test=True):
        self.matching_invoice_line_ids = False
        sml = self.new_stock_picking_ids.move_lines

        # Pass 1: Get all exact match lines done
        for line in self.account_move_id.invoice_line_ids:
            # Propose a random match for line
            same_prod_id = sml.filtered(lambda move: move.product_id == line.product_id)
            same_qty = same_prod_id.filtered(
                lambda sml: self._get_transfer_qty(sml) == line.quantity
            )
            # Case exact match
            if same_qty:
                match_move = same_qty[0]
                sml -= match_move
                self.matching_invoice_line_ids += line
                if not test:
                    line.move_line_ids += match_move
                    if not match_move.quantity_done:
                        match_move.quantity_done = match_move.product_uom_qty

        # Pass 2: Match lines with split pickings
        remaining_inv_lines = (
            self.account_move_id.invoice_line_ids._origin
            - self.matching_invoice_line_ids._origin
        )
        remaining_sm_lines = sml
        for prod_id in remaining_inv_lines.mapped("product_id"):
            prod_line_id = remaining_inv_lines.filtered(
                lambda line: line.product_id == prod_id
            )
            if not test and len(prod_line_id) > 1:
                raise UserError(
                    _(
                        "Unsuported ambiguous choice of invoice lines for split-transfer."
                    )
                )
            invoice_qty = sum(prod_line_id.mapped("quantity"))
            prod_stock_move_ids = remaining_sm_lines.filtered(
                lambda move: move.product_id == prod_id
            )

            transfer_qty = self._get_transfer_qty(prod_stock_move_ids)
            # Match group
            if invoice_qty == transfer_qty:
                match_move = prod_stock_move_ids
                sml -= match_move
                self.matching_invoice_line_ids += prod_line_id
                if not test:
                    prod_line_id.move_line_ids += match_move
                    for move in match_move:
                        if not move.quantity_done:
                            move.quantity_done = move.product_uom_qty

        # Results & Asserts
        self.count_lines_matching = len(self.matching_invoice_line_ids)
        if not test:
            if self.matching_invoice_line_ids != self.account_move_id.invoice_line_ids:
                raise UserError(_("All invoice lines must have a match"))
            if sml:
                raise UserError(_("All selected pickings must be fully matched"))

    @api.onchange("new_stock_picking_ids")
    def _compute_matching(self):
        # TODO: merge with action_exact_match
        """
        Determine whether invoice lines will be fully matched once the current set of
        stock pickings is confirmed.
        """
        self._set_matching_invoice_lines(test=True)

        self._create_new_lines_from_picking()
        self.get_candidate_picking_ids()
        self._create_candidate_lines_from_picking()

    def _create_new_lines_from_picking(self):
        vals = [(6, 0, [])]
        for picking in self.new_stock_picking_ids:
            dic = {
                "picking_id": picking.ids[0],
            }
            vals.append((0, 0, dic))

        values = []
        for picking in self.new_stock_picking_ids:
            dic = {
                "picking_id": picking.ids[0],
            }
            values.append(dic)

        self.new_match_line_ids = False
        self.new_match_line_ids = self.new_match_line_ids.create(values)

    def _create_candidate_lines_from_picking(self):
        values = []
        for picking in self.candidate_stock_picking_ids:
            dic = {
                "picking_id": picking.ids[0],
            }
            values.append(dic)

        self.candidate_match_line_ids = False
        self.candidate_match_line_ids = self.candidate_match_line_ids.create(values)

    @api.onchange("matching_invoice_line_ids", "count_lines_matching")
    def _compute_matching_progress(self):
        if not self.count_lines:
            self.matching_progress = 0
        else:
            self.matching_progress = 100 * self.count_lines_matching / self.count_lines

    # Wizard progress methods
    def reopen_wizard_act_window(self):
        action = self.env.ref(
            "account_move_stock_create.action_account_move_match_picking"
        ).read()[0]
        context = dict(self._context or {})
        action.update({"context": context})
        return action

    def action_select_more_pickings(self):
        context = dict(self._context or {})
        context["default_state"] = "select"
        self = self.with_context(context)

        action = self.reopen_wizard_act_window()
        return action

    # Wizard final actions
    def action_exact_match(self):
        self._set_matching_invoice_lines(test=False)

    def action_create_all(self):
        self.account_move_id.action_generate_pickings_from_invoices()

    def action_match_create(self):
        raise NotImplementedError

    def action_unmatch_all(self):
        aml = self.account_move_id.invoice_line_ids
        for line in aml:
            line.move_line_ids = False


class AccountMoveMatchPickingLine(models.TransientModel):
    _name = "account.move.match.picking.line"
    _description = "Match Picking Line"

    picking_id = fields.Many2one("stock.picking", "Transfer", required=True)

    new_match_wizard_id = fields.Many2one(
        comodel_name="account.move.match.picking",
        ondelete="cascade",
    )

    candidate_match_wizard_id = fields.Many2one(
        comodel_name="account.move.match.picking",
        ondelete="cascade",
    )

    p_line_match = fields.Float(
        string="Matching Lines",
        compute="_compute_p_line_match",
        store=True,
    )

    p_qty_match = fields.Float(
        string="Approx. Qty. Match",
        compute="_compute_p_line_match",
        store=True,
    )

    has_unreserved = fields.Boolean(
        string="Has Unreserved",
        default=False,
    )

    # Picking fields
    priority = fields.Selection(
        related="picking_id.priority",
    )
    partner_id = fields.Many2one(
        string="Contact",
        related="picking_id.partner_id",
    )
    scheduled_date = fields.Datetime(
        string="Scheduled Date",
        related="picking_id.scheduled_date",
    )
    origin = fields.Char(
        string="Source Document",
        related="picking_id.origin",
    )
    state = fields.Selection(
        string="Status",
        related="picking_id.state",
    )

    @api.onchange("new_match_wizard_id", "candidate_match_wizard_id")
    def _compute_p_line_match(self):
        for record in self:

            account_move_id = record._get_account_move()
            if not account_move_id or not record.picking_id:
                record.p_line_match = 0
                record.p_qty_match = 0
                continue

            # From available lines, calculate % of lines with matching prod IDs
            invoice_prod_ids = account_move_id.mapped("invoice_line_ids.product_id")
            stock_prod_ids = record.picking_id.mapped("product_id")
            intersection_ids = invoice_prod_ids & stock_prod_ids
            p_inv_match = len(intersection_ids) / len(invoice_prod_ids)
            p_stock_match = len(intersection_ids) / len(stock_prod_ids)

            if not len(invoice_prod_ids) or not len(stock_prod_ids):
                record.p_line_match = 0
                record.p_qty_match = 0
                continue

            record.p_line_match = 100 * min(p_inv_match, p_stock_match)

            # From filtered matching lines, extract qty matching
            intersection_inv_line_ids = account_move_id.invoice_line_ids.filtered(
                lambda inv_line: inv_line.product_id in intersection_ids
            )
            intersection_stock_line_ids = record.picking_id.move_lines.filtered(
                lambda sm: sm.product_id in intersection_ids
            )
            inv_qty = sum(intersection_inv_line_ids.mapped("quantity"))

            # Choose best from quantity_done vs product_uom_qty
            self._compute_has_unreserved(intersection_stock_line_ids)
            sm_qty = self._get_transfer_qty(intersection_stock_line_ids)

            if not inv_qty or not sm_qty:
                record.p_qty_match = 0
                continue

            record.p_qty_match = 100 * min((inv_qty / sm_qty), (sm_qty / inv_qty))

    def _compute_has_unreserved(self, stock_moves):
        self.has_unreserved = False
        if 0 in stock_moves.mapped("quantity_done"):
            self.has_unreserved = True

    def _get_transfer_qty(self, stock_moves):
        qty = 0
        for move in stock_moves:
            qty += move.quantity_done if move.quantity_done else move.product_uom_qty
        return qty

    def _get_wizard(self):
        if self.new_match_wizard_id:
            return self.new_match_wizard_id
        if self.candidate_match_wizard_id:
            return self.candidate_match_wizard_id
        return False

    def _get_account_move(self):
        if not self._get_wizard() or not self._get_wizard().account_move_id:
            return False
            # TODO: consider using validate/raise
            # raise ValidationError(_("Unable to fetch related account move."))
        return self._get_wizard().account_move_id

    def action_add_line(self):
        new_picking_ids = self._get_wizard().new_stock_picking_ids | self.picking_id
        context = dict(self._context or {})
        context["default_new_stock_picking_ids"] = new_picking_ids.ids
        context["state"] = "main"
        self = self.with_context(context)

        action = self._get_wizard().reopen_wizard_act_window()
        return action
