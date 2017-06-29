# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all invoice and resets the sequence of their invoice line
    """
    env = Environment(cr, SUPERUSER_ID, {})
    invoice = env['account.invoice'].search([])
    invoice._reset_sequence()
