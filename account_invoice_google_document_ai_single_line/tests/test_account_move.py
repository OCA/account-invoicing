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
    def test_00_ocr_process_automatically_update_single_line(self):
        """New method to check single line invoice processing."""
        self.company_data["company"].ocr_google_enabled = "send_automatically"
        self.company_data["company"].google_ocr_invoice_mode = "single_line_total"
        self.company_data["company"].quick_edit_mode = "in_invoices"
        move = self.init_invoice("in_invoice", self.env["res.partner"], "2025-01-01")
        # Asserts that invoice_line is not created.
        self.assertFalse(move.line_ids, "Invoice line is created.")

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
        # Asserts that invoice_line is created.
        self.assertTrue(move.invoice_line_ids, "Invoice line is not created.")
        # Asserts that only one invoice line is created.
        self.assertEqual(
            len(move.invoice_line_ids), 1, "Length of invoice line is not 1."
        )
