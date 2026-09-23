from . import models
from . import report
from odoo.api import Environment
from odoo import SUPERUSER_ID


def assign_proforma_sequences(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    journals = env["account.journal"].search([("type", "=", "sale")])
    for j in journals:
        j._set_pro_forma_sequence_id()
