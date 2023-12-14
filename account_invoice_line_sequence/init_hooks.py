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
    ordering = env["account.invoice.line"]._order
    query = """ update account_invoice_line i
                   set sequence = q.seqnum
                   from (
                      select
                        il.id,
                        il.invoice_id,
                        row_number() over (
                          partition by invoice_id
                          order by %s
                        ) as seqnum
                      from account_invoice_line il
                    ) q
                    where q.id = i.id;
                """
    cr.execute(query, (ordering,))
