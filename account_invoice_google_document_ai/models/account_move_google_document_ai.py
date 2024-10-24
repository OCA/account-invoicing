# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import json
from collections import defaultdict

from google.api_core.client_options import ClientOptions  # pylint: disable=W7936
from google.cloud import documentai_v1 as documentai  # pylint: disable=W7936
from google.oauth2 import service_account  # pylint: disable=W7936

from odoo import _, models
from odoo.tools import float_compare
from odoo.tools.misc import format_amount


class AccountMoveGoogleDocumentAi(models.AbstractModel):
    """
    We want to split the functionality to an abstract model in order to avoid function
    renames and so on. It is cleaner to keep it separate
    """

    _name = "account.move.google.document.ai"
    _description = "Account Move Google Document Ai Functions"

    def _get_ocr_data(self, attachment):
        if attachment.mimetype != "application/pdf":
            return
        company = self.env.company
        client_options = ClientOptions(
            api_endpoint="{}-documentai.googleapis.com".format(
                company.ocr_google_location
            )
        )
        client = documentai.DocumentProcessorServiceClient(
            client_options=client_options,
            credentials=service_account.Credentials.from_service_account_info(
                json.loads(base64.b64decode(company.ocr_google_authentication))
            ),
        )

        name = client.processor_path(
            company.ocr_google_project,
            company.ocr_google_location,
            company.ocr_google_processor,
        )

        encoded_data = attachment.datas
        decoded_data = base64.b64decode(encoded_data)

        # Read the file into memory
        document = {"content": decoded_data, "mime_type": "application/pdf"}
        raw_document = documentai.RawDocument(**document)
        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        # Recognizes text entities in the PDF document
        result = client.process_document(request=request)
        entities = result.document.entities
        return self._parse_ocr_entities(entities)

    def _parse_ocr_float(self, entity):
        if (
            hasattr(entity.normalized_value, "float_value")
            and entity.normalized_value.float_value
        ):
            return entity.normalized_value.float_value
        if (
            hasattr(entity.normalized_value, "integer_value")
            and entity.normalized_value.integer_value
        ):
            return float(entity.normalized_value.integer_value)
        if entity.normalized_value.text:
            return float(entity.normalized_value.text)
        return 0.0

    def _parse_ocr_date(self, entity):
        return entity.normalized_value.text

    def _parse_ocr_text(self, entity):
        return entity.mention_text

    def _parse_ocr_currency(self, entity):
        return (
            self.env["res.currency"]
            .search([("name", "=", entity.normalized_value.text)], limit=1)
            .id
        )

    def _parse_ocr_lines(self, entity):
        line_item_data = {}
        for prop in entity.properties:
            if prop.type_ == "line_item/description":
                line_item_data["name"] = self._parse_ocr_text(prop)
            elif prop.type_ == "line_item/quantity":
                line_item_data["quantity"] = self._parse_ocr_float(prop)
            elif prop.type_ == "line_item/unit_price":
                line_item_data["price_unit"] = self._parse_ocr_float(prop)
        return line_item_data

    def _control_amount(self, invoice, field, value):
        if (
            float_compare(
                value, invoice[field], precision_rounding=invoice.currency_id.rounding
            )
            != 0
        ):
            return _("%s is not coincident (%s - %s)") % (
                invoice._fields[field].string,
                format_amount(self.env, value, invoice.currency_id),
                format_amount(self.env, invoice[field], invoice.currency_id),
            )

    def _ocr_field_control(self):
        return {
            "amount_total": self._control_amount,
            "amount_untaxed": self._control_amount,
            "amount_tax": self._control_amount,
        }

    def _ocr_field_parser(self):
        return {
            "total_amount": (
                "amount_total",
                self._parse_ocr_float,
                "control",
            ),
            "net_amount": (
                "amount_untaxed",
                self._parse_ocr_float,
                "control",
            ),
            "total_tax_amount": (
                "amount_tax",
                self._parse_ocr_float,
                "control",
            ),
            "invoice_date": ("invoice_date", self._parse_ocr_date, "write"),
            "due_date": ("invoice_date_due", self._parse_ocr_date, "write"),
            "invoice_id": ("ref", self._parse_ocr_text, "write"),
            "supplier_name": ("name", self._parse_ocr_text, "partner"),
            "supplier_address": ("address", self._parse_ocr_text, "partner"),
            "supplier_email": ("email", self._parse_ocr_text, "partner"),
            "supplier_phone": ("phone", self._parse_ocr_text, "partner"),
            "supplier_tax_id": ("vat", self._parse_ocr_text, "partner"),
            "supplier_iban": ("iban", self._parse_ocr_text, "partner"),
            "receiver_tax_id": ("vat", self._parse_ocr_text, "company"),
            "receiver_name": ("name", self._parse_ocr_text, "company"),
            "receiver_address": ("address", self._parse_ocr_text, "company"),
            "currency": ("currency_id", self._parse_ocr_currency, "write"),
            "line_item": ("invoice_line_ids", self._parse_ocr_lines, "lines"),
        }

    def _parse_ocr_entities(self, entities):
        result = defaultdict(lambda: {})
        field_parsers = self._ocr_field_parser()
        if entities:
            for entity in entities:
                if entity.type in field_parsers:
                    field_parser = field_parsers[entity.type]
                    name = field_parser[0]
                    parser = field_parser[1]
                    key = field_parser[2]
                    value = parser(entity)
                    if key == "lines":
                        if name not in result[key]:
                            result[key][name] = []
                        result[key][name].append(value)
                    else:
                        result[key][name] = value
        return self._postprocess_ocr_data(result)

    def _get_ocr_partner(self, partner_data):
        if partner_data.get("vat"):
            partner = self.env["res.partner"].search(
                [("vat", "=", partner_data["vat"])], limit=1
            )
            if partner:
                return partner
        if partner_data.get("name"):
            partner = self.env["res.partner"].search(
                [("name", "=", partner_data["name"])], limit=1
            )
            if partner:
                return partner

    def _postprocess_ocr_data(self, result):
        for key, value in result.get("lines", {}).items():
            if key == "invoice_line_ids":
                result["write"]["invoice_line_ids"] = []
                line_fields = self.env["account.move.line"]._fields
                for line in value:
                    line_vals = line.copy()
                    for key in line:
                        if key not in line_fields:
                            line_vals.pop(key)
                    result["write"]["invoice_line_ids"].append((0, 0, line_vals))
            else:
                result["write"][key] = value
        if result.get("partner"):
            partner = self._get_ocr_partner(result.get("partner"))
            if partner:
                result["write"]["partner_id"] = partner.id
        return result

    def _update_invoice_from_attachment(self, attachment, invoice):
        invoice_data = self._get_ocr_data(attachment)
        if invoice_data:
            invoice.line_ids.unlink()
            self._process_invoice(invoice, invoice_data, [])
            return True

    def _process_invoice(self, invoice, invoice_data, messages):
        if invoice_data["context"]:
            invoice = invoice.with_context(**invoice_data["context"])
        if invoice_data["write"]:
            invoice.write(invoice_data["write"])
        field_controls = self._ocr_field_control()
        for field, value in invoice_data["control"].items():
            message = field_controls[field](invoice, field, value)
            if message is not None:
                messages.append(message)
        if messages:
            invoice.message_post(body="<br/>".join(messages))

    def _get_invoice_company(self, invoice_data):
        if invoice_data["company"]:
            if invoice_data["company"].get("vat"):
                company = self.env["res.company"].search(
                    [("vat", "like", invoice_data["company"].get("vat"))]
                )
                if company:
                    return company
        return False

    def _get_invoice(self, invoice_data):
        """
        We want to maintain a hook because it might be interesting for
        contracts, an existent invoice in draft, with but not the number.
        """
        company = self._get_invoice_company(invoice_data) or self.env.company
        context = {}
        if invoice_data["context"]:
            context.update(invoice_data["context"])
        invoice = (
            self.env["account.move"]
            .with_company(company.id)
            .with_context(**context)
            .create({})
        )
        invoice.flush()
        return invoice

    def _create_invoice_from_attachment(self, attachment):
        invoice_data = self._get_ocr_data(attachment)
        if not invoice_data:
            return
        invoice = self._get_invoice(invoice_data)
        self._process_invoice(invoice, invoice_data, [])
        return invoice
