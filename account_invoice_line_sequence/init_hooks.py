# Copyright 2017 Forgeflow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(env):
    """
    Fetches all invoice and resets the sequence of their invoice line
    """
    invoice = env["account.move"].search([])
    invoice._reset_sequence()
