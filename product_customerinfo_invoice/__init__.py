# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models

from openupgradelib import openupgrade


def _product_customerinfo_invoice_pre_init_hook(env):
    if openupgrade.is_module_installed(
        env.cr, "product_supplierinfo_for_customer_invoice"
    ):
        openupgrade.update_module_names(
            env.cr,
            [
                (
                    "product_supplierinfo_for_customer_invoice",
                    "product_customerinfo_invoice",
                ),
            ],
            merge_modules=True,
        )
