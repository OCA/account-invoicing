from unittest.mock import patch

from google.auth import credentials as ga_credentials
from google.cloud import documentai_v1
from google.cloud.documentai_v1.types import document_processor_service
from google.oauth2 import service_account
from google.protobuf import json_format

from odoo import tools
from odoo.tests import tagged

from odoo.addons.account_invoice_google_document_ai.tests.test_google_document_ai import (
    TestGoogleDocumentAi,
)


@tagged("post_install", "-at_install")
class TestGoogleDocumentAiSingleLine(TestGoogleDocumentAi):
    def test_00_log_ocr_entities_debug(self):
        """New method to check if OCR entities are logged as JSON attachment in the
        chatter when the company setting is enabled."""
        self.company_data["company"].ocr_google_enabled = "send_manual"
        self.company_data["company"].log_ocr_entities_debug = True
        move = self.init_invoice("in_invoice", self.env["res.partner"], "2023-01-01")
        # Asserts that move line is not created.
        self.assertFalse(move.line_ids, "Move lines are created.")
        move.message_post(
            attachments=[
                (
                    "filename.pdf",
                    bytes(
                        tools.file_open(
                            "account/static/demo/in_invoice_yourcompany_demo_1.pdf",
                            mode="rb",
                        ).read()
                    ),
                )
            ]
        )
        with patch.object(
            service_account.Credentials, "from_service_account_info"
        ) as factory, patch.object(
            documentai_v1.DocumentProcessorServiceClient, "process_document"
        ) as process:
            factory.return_value = ga_credentials.AnonymousCredentials()
            resp = document_processor_service.ProcessResponse()
            response = document_processor_service.ProcessResponse.pb(resp)
            json_format.Parse(
                tools.file_open(
                    "account_invoice_google_document_ai/tests/result.json",
                )
                .read()
                .encode("UTF-8"),
                response,
                ignore_unknown_fields=True,
            )
            process.return_value = resp
            move.ocr_process()

        # Assert that invoice lines are created
        self.assertTrue(move.invoice_line_ids, "Invoice lines are not created.")

        # Assert that the OCR entities JSON attachment is created
        attachment = self.env["ir.attachment"].search(
            [("res_id", "=", move.id), ("res_model", "=", "account.move")], limit=1
        )
        self.assertTrue(attachment, "OCR entities attachment was not created.")
        self.assertTrue(
            attachment.name.startswith("ocr_entities_"), "Attachment name is incorrect."
        )
        self.assertEqual(
            attachment.mimetype, "application/json", "Attachment mimetype is incorrect."
        )

    def test_01_log_ocr_entities_debug_disabled(self):
        """New method to check that OCR entities are not logged as JSON attachment in the
        chatter when the company setting is disabled."""
        self.company_data["company"].ocr_google_enabled = "send_automatically"
        self.company_data["company"].log_ocr_entities_debug = False
        move = self.init_invoice("in_invoice", self.env["res.partner"], "2025-01-01")
        # Asserts that invoice lines are not created.
        self.assertFalse(move.line_ids, "Invoice lines are created.")

        with patch.object(
            service_account.Credentials, "from_service_account_info"
        ) as factory, patch.object(
            documentai_v1.DocumentProcessorServiceClient, "process_document"
        ) as process:
            factory.return_value = ga_credentials.AnonymousCredentials()
            resp = document_processor_service.ProcessResponse()
            response = document_processor_service.ProcessResponse.pb(resp)
            json_format.Parse(
                tools.file_open("account_invoice_google_document_ai/tests/result.json")
                .read()
                .encode("UTF-8"),
                response,
                ignore_unknown_fields=True,
            )
            process.return_value = resp
            move.message_post(
                attachments=[
                    (
                        "filename.pdf",
                        bytes(
                            tools.file_open(
                                "account/static/demo/in_invoice_yourcompany_demo_1.pdf",
                                mode="rb",
                            ).read()
                        ),
                    )
                ]
            )
        # Assert that invoice lines are created
        self.assertTrue(move.invoice_line_ids, "Invoice lines are not created.")
        # Assert that the OCR entities JSON attachment is not created
        attachment = self.env["ir.attachment"].search(
            [("res_id", "=", move.id), ("res_model", "=", "account.move")], limit=1
        )
        self.assertTrue(attachment, "OCR entities attachment was not created.")
        self.assertFalse(
            attachment.name.startswith("ocr_entities_"), "Attachment name is incorrect."
        )
