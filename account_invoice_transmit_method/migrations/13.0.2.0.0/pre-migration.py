# Copyright 2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# I don't use openupgrade.convert_to_company_dependent
# because it obliges to change the field name

from datetime import datetime

from odoo import SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return

    partnerid2customertrid = {}
    cr.execute(
        "SELECT id, customer_invoice_transmit_method_id "
        "FROM res_partner "
        "WHERE customer_invoice_transmit_method_id IS NOT null"
    )
    for entry in cr.fetchall():
        partnerid2customertrid[entry[0]] = entry[1]
    partnerid2suppliertrid = {}
    cr.execute(
        "SELECT id, supplier_invoice_transmit_method_id "
        "FROM res_partner "
        "WHERE supplier_invoice_transmit_method_id IS NOT null"
    )
    for entry in cr.fetchall():
        partnerid2suppliertrid[entry[0]] = entry[1]
    cr.execute(
        "SELECT id FROM ir_model_fields "
        "WHERE name='customer_invoice_transmit_method_id' AND model='res.partner'"
    )
    customer_field_id = cr.fetchone()[0]

    cr.execute(
        "SELECT id FROM ir_model_fields "
        "WHERE name='supplier_invoice_transmit_method_id' AND model='res.partner'"
    )
    supplier_field_id = cr.fetchone()[0]

    cr.execute("SELECT id FROM res_company")
    now = datetime.utcnow()
    for entry in cr.fetchall():
        company_id = entry[0]

        for partner_id, mode_id in partnerid2customertrid.items():
            cr.execute(
                """
                INSERT INTO ir_property (
                create_uid, create_date, write_uid, write_date,
                fields_id, company_id, res_id, value_reference, name, type)
                VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                'customer_invoice_transmit_method_id', 'many2one')
                """,
                (
                    SUPERUSER_ID,
                    now,
                    SUPERUSER_ID,
                    now,
                    customer_field_id,
                    company_id,
                    "res.partner,%d" % partner_id,
                    "transmit.method,%d" % mode_id,
                ),
            )

        for partner_id, mode_id in partnerid2suppliertrid.items():
            cr.execute(
                """
                INSERT INTO ir_property (
                create_uid, create_date, write_uid, write_date,
                fields_id, company_id, res_id, value_reference, name, type)
                VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                'supplier_invoice_transmit_method_id', 'many2one')
                """,
                (
                    SUPERUSER_ID,
                    now,
                    SUPERUSER_ID,
                    now,
                    supplier_field_id,
                    company_id,
                    "res.partner,%d" % partner_id,
                    "transmit.method,%d" % mode_id,
                ),
            )
