# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import urllib
from unittest import mock

import qrcode
import requests
import urllib3
from urllib3._collections import HTTPHeaderDict

from odoo.tests import Form
from odoo.tests.common import TransactionCase


def get_image():
    params = {
        "D": "Payment",
        "A": "3090",
        "R": "test",
    }
    return qrcode.make(
        "https://payconiq.com/t/1/1234567890?" + urllib.parse.urlencode(params)
    )


def mocked_requests_get(*args, **kwargs):
    headers = HTTPHeaderDict({"Content-Type": "image/png"})
    http_response = urllib3.response.HTTPResponse(
        request_method="GET", headers=headers, status=200
    )

    response = requests.Response()
    response.status_code = 200
    response.raw = http_response
    return response


class TestAccountInvoicePayconiq(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a Luxembourgish company with at least a bank account
        cls.company = cls.env["res.company"].create(
            {
                "name": "Lux Company",
            }
        )
        cls.env["account.chart.template"].browse(1).with_company(
            cls.company
        ).try_loading()
        cls.company.currency_id = cls.env.ref("base.EUR")
        pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist EUR",
                "company_id": cls.company.id,
                "currency_id": cls.env.ref("base.EUR").id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.env["res.partner.bank"].create(
            {
                "acc_number": "LU 28 001 9400644750000",
                "partner_id": cls.company.partner_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.company.qr_code = True
        # Set the Payconiq profile
        cls.company.payconiq_qr_profile_id = "1234567890"
        cls.account_move = cls.env["account.move"]
        cls.invoice = cls.env["account.move"].create(
            {
                "name": "Test Invoice",
                "move_type": "out_invoice",
                "currency_id": cls.company.currency_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "My Lux User",
                "login": "lux_user",
                "company_id": cls.company.id,
                "company_ids": [(4, cls.company.id)],
            }
        )
        cls.user.groups_id |= cls.env.ref("account.group_account_manager")
        # Change Environment to make all operations in user's Lux company
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, user=cls.user)
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "test partner", "property_product_pricelist": pricelist.id}
        )
        invoice_form = Form(cls.invoice)
        invoice_form.partner_id = cls.partner

        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Test invoice line"
            line_form.price_unit = 30.1
            line_form.tax_ids.clear()
        cls.invoice = invoice_form.save()
        cls.invoice.qr_code_method = "payconiq_qr"

    def test_payconiq(self):
        with mock.patch("requests.get", side_effect=mocked_requests_get), mock.patch(
            "PIL.Image.open"
        ) as image_mock:
            image_mock.return_value = get_image()
            url = self.invoice._generate_qr_code()

        self.assertTrue(url)
        self.assertIn(
            "data:image/png;base64",
            url,
        )
