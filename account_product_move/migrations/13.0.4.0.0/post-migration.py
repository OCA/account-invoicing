# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Debit and credit now are in the effective currency."""
from openupgradelib.openupgrade import column_exists

# pylint: disable=invalid-name,protected-access
from odoo.api import SUPERUSER_ID, Environment


def _update_debit_credit(env):
    """Update debit and credit to amount in effective currency.

    Before debit and credit where always in the company currency. Now
    they will be in the effective currency for the account.product.move.line.

    Conversion will only be done on creating actual moves from the configuration.
    """
    line_model = env["account.product.move.line"]
    if not column_exists(env.cr, line_model._table, "amount_currency"):
        return
    lines = line_model.search(
        [
            ("currency_id", "!=", False),
            ("amount_currency", "!=", False),
            ("amount_currency", "!=", 0.0),
        ]
    )
    for line in lines:
        if line.amount_currency < 0.0:
            credit = 0.0 - line.amount_currency
            debit = 0.0
        else:
            credit = 0.0
            debit = line.amount_currency
        line.write(
            {
                "debit": debit,
                "credit": credit,
                "amount_currency": 0.0,  # Prevent repeated update of debit and credit.
            }
        )


def migrate(cr, version):
    """Replace capability of printing order lines with printing any template."""
    if not version:
        return
    env = Environment(cr, SUPERUSER_ID, {})
    _update_debit_credit(env)
