# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_to_company_dependent(
        env=env,
        model_name="res.partner",
        origin_field_name="customer_invoice_transmit_method_id",
        destination_field_name="customer_invoice_transmit_method_id",
    )
    openupgrade.convert_to_company_dependent(
        env=env,
        model_name="res.partner",
        origin_field_name="supplier_invoice_transmit_method_id",
        destination_field_name="supplier_invoice_transmit_method_id",
    )
