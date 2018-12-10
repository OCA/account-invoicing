# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version=None):
    cr.execute(
        "alter table if exists hr_timesheet_invoice_factor "
        "rename to account_invoice_analytic_line_discount"
    )
    cr.execute(
        "alter table if exists account_invoice_analytic_line_discount "
        "rename factor to discount"
    )
    cr.execute(
        "alter table if exists hr_timesheet_invoice_factor_id_seq "
        "rename to account_invoice_analytic_line_discount_id_seq"
    )
