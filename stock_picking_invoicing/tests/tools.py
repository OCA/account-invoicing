# Copyright (C) 2026-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form


def create_with_form_product_product(env, values):
    with Form(env["product.product"]) as product:
        product.name = values.get("name")
        product.lst_price = values.get("lst_price")
        product.taxes_id = values.get("taxes_id")
        product.supplier_taxes_id = values.get("supplier_taxes_id")
        product.property_account_income_id = values.get("property_account_income_id")
        product.standard_price = values.get("standard_price")
        product.type = values.get("type")
        if values.get("type") == "consu":
            product.is_storable = values.get("is_storable")
            if "invoice_policy" in env["product.product"]._fields:
                product.invoice_policy = values.get("invoice_policy")
        product.sale_ok = True
        product.purchase_ok = True

    return product.save()


def create_with_form_stock_picking(env, values, line_values=False):
    with Form(env["stock.picking"]) as picking:
        picking.partner_id = values.get("partner_id")
        picking.picking_type_id = values.get("picking_type_id")
        for value in line_values:
            with picking.move_ids_without_package.new() as line:
                line.product_id = value.get("product_id")
                line.product_uom_qty = value.get("product_uom_qty")

    return picking.save()


def create_with_form_inv_onshipping(env, pickings):
    with Form(
        env["stock.invoice.onshipping"].with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
    ) as wzd_inv:
        wzd_inv.group = "partner_product"
        result = wzd_inv.save()

    result.action_generate()

    return pickings.mapped("invoice_ids")


def create_with_form_return_picking(env, picking):
    return_wizard_form = Form(
        env["stock.return.picking"].with_context(
            active_id=picking.id, active_model="stock.picking"
        )
    )
    return_wizard_form.invoice_state = "2binvoiced"
    return_wizard = return_wizard_form.save()
    return_wizard.product_return_moves[0].quantity = 1
    result_wizard = return_wizard.action_create_returns()
    return env["stock.picking"].browse(result_wizard.get("res_id"))


def create_with_form_pck_backorder(env, picking):
    res_dict_for_back_order = picking.button_validate()
    backorder_wizard = Form(
        env[res_dict_for_back_order["res_model"]].with_context(
            **res_dict_for_back_order["context"]
        )
    ).save()
    backorder_wizard.process()

    return env["stock.picking"].search([("backorder_id", "=", picking.id)])
