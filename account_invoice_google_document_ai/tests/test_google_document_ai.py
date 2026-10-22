# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from unittest.mock import patch

from google.auth import credentials as ga_credentials
from google.cloud import documentai_v1
from google.cloud.documentai_v1.types import document_processor_service
from google.oauth2 import service_account
from google.protobuf import json_format

from odoo import tools
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestGoogleDocumentAi(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company_data["company"].write(
            {
                "ocr_google_enabled": "send_manual",
                "ocr_google_location": "eu",
                "ocr_google_processor": "processor",
                "ocr_google_project": "project",
                "ocr_google_authentication": base64.b64encode(b"{}"),
                "ocr_google_authentication_name": "filename.json",
            }
        )

    def test_ocr_process_manually(self):
        self.company_data["company"].ocr_google_enabled = "send_manual"
        move = self.init_invoice("in_invoice", self.env["res.partner"], "2023-01-01")
        self.assertFalse(move.line_ids)
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
        self.assertTrue(move.invoice_line_ids)

    def test_ocr_process_automatically(self):
        self.company_data["company"].ocr_google_enabled = "send_automatically"
        move = self.init_invoice("in_invoice", self.env["res.partner"], "2025-01-01")
        self.assertFalse(move.line_ids)

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
        self.assertTrue(move.invoice_line_ids)

    def test_ocr_process_automatically_create(self):
        self.company_data["company"].ocr_google_enabled = "send_automatically"
        attachment = self.env["ir.attachment"].create(
            {
                "name": "filename.pdf",
                "datas": base64.b64encode(
                    bytes(
                        tools.file_open(
                            "account/static/demo/in_invoice_yourcompany_demo_1.pdf",
                            mode="rb",
                        ).read()
                    )
                ),
            }
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
                tools.file_open("account_invoice_google_document_ai/tests/result.json")
                .read()
                .encode("UTF-8"),
                response,
                ignore_unknown_fields=True,
            )
            process.return_value = resp
            self.env["account.journal"].with_context(
                default_move_type="in_invoice"
            )._create_document_from_attachment(attachment.ids)
        # self.assertTrue(move.invoice_line_ids)
