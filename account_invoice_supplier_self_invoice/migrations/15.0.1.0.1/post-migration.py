# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    companies = env["res.company"].search([]).ids
    main_company = env.ref("base.main_company", False) or companies[0]
    openupgrade.logged_query(
        env.cr,
        """
        SELECT id, self_invoice_sequence_id, company_id
        FROM res_partner
        WHERE self_invoice
        """,
    )
    for row in env.cr.fetchall():
        partner = env["res.partner"].browse(row[0])
        partner_companies = companies
        if row[2] is not None:
            partner_companies = [row[2]]
        for company in partner_companies:
            partner.with_company(company).write({"self_invoice": True})
        partner.with_company(row[2] or main_company).write(
            {"self_invoice_sequence_id": row[1]}
        )
