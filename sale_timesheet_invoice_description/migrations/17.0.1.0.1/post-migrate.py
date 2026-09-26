from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    res_config_obj = env["res.config.settings"]
    default_values = res_config_obj.default_get(list(res_config_obj.fields_get()))
    timesheet_invoice_description = default_values.get(
        "default_timesheet_invoice_description"
    )
    if not timesheet_invoice_description:
        default_values.update({"default_timesheet_invoice_description": "000"})
        res_config_obj.create(default_values).execute()
        timesheet_invoice_description = default_values.get(
            "default_timesheet_invoice_description"
        )
    sale_orders = (
        env["sale.order"]
        .with_context(active_test=False)
        .search(
            [
                ("timesheet_invoice_description", "=", False),
            ]
        )
    )
    sale_orders.write({"timesheet_invoice_description": timesheet_invoice_description})
