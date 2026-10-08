# Copyright (C) 2026-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form


def create_with_form_product_combo(env, values, line_values):
    with Form(env["product.combo"]) as combo:
        combo.name = values.get("name")
        for ln_value in line_values:
            with combo.combo_item_ids.new() as combo_line:
                combo_line.product_id = ln_value.get("product_id")

    return combo.save()


def create_with_form_sale_order(env, values, line_values=False):
    with Form(
        env["sale.order"]
        .with_company(values.get("company_id"))
        .with_context(
            mail_notrack=True,
            mail_create_nolog=True,
        )
    ) as sale:
        sale.partner_id = values.get("partner_id")
        sale.partner_invoice_id = values.get("partner_invoice_id")
        sale.partner_shipping_id = values.get("partner_shipping_id")
        sale.pricelist_id = values.get("pricelist_id")
        sale.client_order_ref = values.get("client_order_ref")
        sale.incoterm = values.get("incoterm")
        sale.note = values.get("note")
        sale.company_id = values.get("company_id")
        for value in line_values:
            with sale.order_line.new() as line:
                if value.get("display_type"):
                    line.name = value.get("name")
                    line.display_type = value.get("display_type")
                else:
                    line.product_id = value.get("product_id")
                    line.product_uom_qty = value.get("product_uom_qty")

    return sale.save()


def create_with_form_sale_adv_pay_inv(env, sale_order, values):
    with Form(
        env["sale.advance.payment.inv"].with_context(
            active_model="sale.order",
            active_id=sale_order.id,
            active_ids=sale_order.ids,
        )
    ) as wzd:
        wzd.advance_payment_method = values.get("advance_payment_method")
        wzd.amount = values.get("amount")
        result_wzd = wzd.save()
        result_wzd.create_invoices()

    return sale_order.mapped("invoice_ids")


def create_with_form_account_payment(env, invoice, values):
    with Form(
        env["account.payment.register"].with_context(
            active_model="account.move",
            active_ids=invoice.ids,
        )
    ) as wzd:
        wzd.journal_id = values.get("journal_id")
        wzd.amount = values.get("amount")

    return wzd.save()._create_payments()


def get_tested_module_names(env, module_name):
    """Return ``module_name`` and the names of its (transitive) dependencies.

    Used to restrict the fields compared by the tests to the ones provided by
    the modules under test: other installed modules (localizations, ...) add
    their own fields on the same models and are set by their own glue modules,
    tested by their own tests.
    """
    dependencies = {
        module.name: module.dependencies_id.mapped("name")
        for module in env["ir.module.module"].search([])
    }
    module_names, todo = set(), [module_name]
    while todo:
        name = todo.pop()
        if name in module_names:
            continue
        module_names.add(name)
        todo.extend(dependencies.get(name, []))
    return module_names
