# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiXmlUBL20(models.AbstractModel):

    _inherit = "account.edi.xml.ubl_20"

    def _import_fill_invoice_form(self, journal, tree, invoice, qty_factor):
        invoice = invoice.with_context(no_purchase_set=True)
        res = super()._import_fill_invoice_form(journal, tree, invoice, qty_factor)
        if journal.type != "purchase":
            return res
        invoice_origin_node = tree.find("./{*}OrderReference/{*}ID")
        if invoice_origin_node is None:
            return res
        order_ref = invoice_origin_node.text
        self._match_invoice_to_purchase_order(invoice, order_ref)
        return res

    def _match_invoice_to_purchase_order(self, invoice, order_ref):
        purchase_order = self.env["purchase.order"].search(
            [
                "|",
                ("name", "=", order_ref),
                ("partner_ref", "=", order_ref),
                ("state", "in", ("purchase", "done")),
            ],
            limit=1,
        )
        if not purchase_order:
            return False
        for invoice_line in invoice.invoice_line_ids:
            self._match_invoice_line_to_purchase_order_line(
                invoice_line, purchase_order.order_line
            )
        return True

    def _match_invoice_line_to_purchase_order_line(self, invoice_line, purchase_lines):
        if invoice_line.purchase_line_id:
            return False
        product = self._get_matching_product(invoice_line)
        purchase_line = purchase_lines.filtered(lambda line: line.product_id == product)
        invoice_line._set_product(product)
        invoice_line.purchase_line_id = purchase_line
        return True

    def _get_matching_product(self, invoice_line):
        product_model = self.env["product.product"]
        if invoice_line.product_id:
            return invoice_line.product_id
        product_name = invoice_line.name
        if not product_name:
            return product_model
        product = product_model.search([("name", "=", product_name)])
        if product:
            return product
        partner = invoice_line.move_id.partner_id
        if not partner:
            return product_model
        supplierinfo = self.env["product.supplierinfo"].search(
            [
                ("product_name", "=", product_name),
                ("partner_id", "=", invoice_line.move_id.partner_id.id),
            ],
            limit=1,
        )
        if not supplierinfo:
            return product_model
        if supplierinfo.product_id:
            return supplierinfo.product_id
        if (
            supplierinfo.product_tmpl_id
            and len(supplierinfo.product_tmpl_id.product_variant_ids) == 1
        ):
            return supplierinfo.product_tmpl_id.product_variant_ids
        return product_model

    def _import_fill_invoice_line_form(
        self, journal, tree, invoice, invoice_line, qty_factor
    ):
        res = super()._import_fill_invoice_line_form(
            journal, tree, invoice, invoice_line, qty_factor
        )
        supplier_product_code = self._find_value(
            "./cac:Item/cac:SellersItemIdentification/cbc:ID", tree
        )
        if invoice_line.product_id or not supplier_product_code:
            return res
        product_sinfo = self.env["product.supplierinfo"].search(
            [
                ("product_code", "=", supplier_product_code),
                ("partner_id", "=", invoice.partner_id.id),
            ],
            limit=1,
        )
        if product_sinfo and product_sinfo.product_id:
            invoice_line._set_product(product_sinfo.product_id)
        if (
            product_sinfo
            and product_sinfo.product_tmpl_id
            and len(product_sinfo.product_tmpl_id.product_variant_ids) == 1
        ):
            invoice_line._set_product(product_sinfo.product_tmpl_id.product_variant_ids)
        if not invoice_line.product_id and supplier_product_code:
            # if no match for the product and the supplier_product_code is defined
            # fill it into the invoice_line so it can used at manual match
            invoice_line.supplier_product_code = supplier_product_code
        return res
