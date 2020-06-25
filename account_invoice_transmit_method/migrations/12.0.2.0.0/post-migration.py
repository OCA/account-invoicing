# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        " SELECT id, supplier_invoice_transmit_method_id, "
        " customer_invoice_transmit_method_id "
        " FROM res_partner "
        " WHERE supplier_invoice_transmit_method_id IS NOT NULL or "
        " customer_invoice_transmit_method_id IS NOT NULL "
    )
    for r in cr.fetchall():
        vals = {}
        if r[1]:
            vals['supplier_invoice_transmit_method_ids'] = [(4, r[1])]
        if r[2]:
            vals['customer_invoice_transmit_method_ids'] = [(4, r[2])]
        env['res.partner'].browse(r[0]).write(vals)
    cr.execute(
        "SELECT id, transmit_method_id FROM account_invoice "
        "WHERE transmit_method_id IS NOT NULL")
    for r in cr.fetchall():
        env['account.invoice'].browse(r[0]).transmit_method_ids = [(4, r[1])]
    env.ref('account_invoice_transmit_method.mail').send_mail = True
