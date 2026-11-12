# Copyright (C) 2026-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form


def create_with_form_res_partner(env, values):
    with Form(env["res.partner"]) as partner:
        partner.name = values.get("name")
        partner.category_id = values.get("category_id")
        partner.street = values.get("street")
        partner.city = values.get("city")
        partner.country_id = values.get("country_id")
        partner.state_id = values.get("state_id")
        partner.zip = values.get("zip")
        partner.email = values.get("email")
        partner.phone = values.get("phone")
        partner.website = values.get("website")
        partner.vat = values.get("vat")
        if values.get("type"):
            partner.type = values.get("type")
        if values.get("parent_id"):
            partner.parent_id = values.get("parent_id")
    return partner.save()


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
        for value in line_values:
            with sale.order_line.new() as line:
                if value.get("display_type"):
                    line.name = value.get("name")
                    line.display_type = value.get("display_type")
                else:
                    line.product_id = value.get("product_id")
                    line.product_uom_qty = value.get("product_uom_qty")

    sale_order = sale.save()
    sale_order.write(
        {
            "partner_invoice_id": values["partner_invoice_id"].id,
            "partner_shipping_id": values["partner_shipping_id"].id,
            "pricelist_id": values["pricelist_id"].id,
            "client_order_ref": values["client_order_ref"],
            "incoterm": values["incoterm"].id,
            "note": values["note"],
            "company_id": values["company_id"].id,
        }
    )
    sale_order.fiscal_position_id = False
    sale_order._recompute_taxes()
    return sale_order


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
    payment_register = (
        env["account.payment.register"]
        .with_context(
            active_model="account.move",
            active_ids=invoice.ids,
        )
        .create(
            {
                "journal_id": values["journal_id"].id,
                "amount": values["amount"],
            }
        )
    )
    return payment_register._create_payments()
