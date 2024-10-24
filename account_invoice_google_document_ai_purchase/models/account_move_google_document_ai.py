# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tests.common import Form


class AccountMoveGoogleDocumentAi(models.AbstractModel):

    _inherit = "account.move.google.document.ai"

    def _ocr_field_parser(self):
        result = super()._ocr_field_parser()
        result.update(
            {
                "purchase_order": (
                    "purchase_order",
                    self._parse_ocr_text,
                    "purchase_order",
                ),
            }
        )
        return result

    def _parse_ocr_lines(self, entity):
        line_item_data = super()._parse_ocr_lines(entity)
        for prop in entity.properties:
            if prop.type_ == "line_item/purchase_order":
                line_item_data["purchase_order"] = self._parse_ocr_text(prop)
        return line_item_data

    def _purchase_order_domain(self, purchase_order, invoice_data):
        domain = [
            ("name", "=", purchase_order),
            ("state", "in", ["purchase", "done"]),
            ("invoice_status", "=", "to invoice"),
        ]
        if invoice_data.get("write", {}).get("partner_id"):
            partner = self.env["res.partner"].browse(
                invoice_data.get("write", {}).get("partner_id")
            )
            domain.append(
                (
                    "partner_id.commercial_partner_id",
                    "=",
                    partner.commercial_partner_id.id,
                )
            )
        return domain

    def _postprocess_ocr_data(self, result):
        new_result = super()._postprocess_ocr_data(result)
        purchase_orders = set()
        messages = []
        if new_result.get("purchase_order"):
            purchase_orders.add(new_result["purchase_order"]["purchase_order"])
        for line in new_result.get("lines", {}).get("invoice_line_ids", []):
            if line.get("purchase_order"):
                purchase_orders.add(line.get("purchase_order"))
        if purchase_orders:
            po = self.env["purchase.order"]
            for purchase_order in purchase_orders:
                new_po = self.env["purchase.order"].search(
                    self._purchase_order_domain(purchase_order, new_result)
                )
                if not new_po:
                    messages.append(
                        _("Purchase Order %s cannot be processed") % purchase_order
                    )
                po |= new_po
            new_result["purchase_order_ids"] = po
            new_result["purchase_order_errors"] = messages
        return new_result

    def _get_invoice_company(self, invoice_data):
        company = super()._get_invoice_company(invoice_data)
        if not company and invoice_data["purchase_order_ids"]:
            new_company = invoice_data["purchase_order_ids"].mapped("company_id")
            if len(new_company) == 1:
                return new_company
        return company

    def _process_purchase_invoice(self, invoice, invoice_data, purchase_orders):
        with Form(invoice) as f:
            for purchase_order in purchase_orders:
                f.purchase_id = purchase_order

    def _process_invoice(self, invoice, invoice_data, messages):
        messages += invoice_data.get("purchase_order_errors", [])
        for po in invoice_data.get("purchase_order_ids", []):
            invoice_data["write"]["invoice_line_ids"] = []
            self._process_purchase_invoice(invoice, invoice_data, po)
        return super()._process_invoice(invoice, invoice_data, messages)
