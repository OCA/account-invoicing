# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io
import urllib

import requests
from PIL import Image

from odoo import _, api, models
from odoo.tools.image import image_data_uri

PAYCONIQ_URL = "https://payconiq.com/t/1/"
PAYCONIQ_QR_URL = "https://portal.payconiq.com/qrcode"


class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    @api.model
    def _get_available_qr_methods(self):
        rslt = super()._get_available_qr_methods()
        rslt.append(("payconiq_qr", _("Payconiq QR"), 19))
        return rslt

    def _get_payconiq_qr_amount(self, amount):
        """
        Payconiq is awaiting an amount in eurocents. So,
        if the amount is for instance 141.9, reformat to float with
        two decimals => 141.90, then remove decimal dot.
        """
        return f"{amount*100:.0f}"

    def _get_qr_code_generation_params(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        """
        https://developer.payconiq.com/online-payments-dock/#creating-the-payconiq-qr-code77

        """
        if qr_method == "payconiq_qr":
            return {
                "payconiq_qr": True,
                "D": "Payment",
                "A": self._get_payconiq_qr_amount(amount),
                "R": structured_communication
                if structured_communication
                else free_communication,
            }
        return super()._get_qr_code_generation_params(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def _get_qr_code_url(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        params = self._get_qr_code_generation_params(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )
        if params and params.get("payconiq", False):
            params.pops("payconiq_qr")
            return urllib.parse.urlencode(params)
        return super()._get_qr_code_url(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def _eligible_for_qr_code(self, qr_method, debtor_partner, currency):
        if qr_method == "payconiq_qr":
            return (
                currency.name == "EUR"
                and self.acc_type == "iban"
                and self.sanitized_acc_number[:2] in ["LU"]
            )
        return super()._eligible_for_qr_code(qr_method, debtor_partner, currency)

    def _get_qr_code_base64(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        """
        The url to get QR code image from Payconiq is composed by several parameters:
            - The type of the image
            - The image size
            - The redirection url (to launch the payconiq application - this is the url
              inside the QR code itself)
        """
        params = self._get_qr_code_generation_params(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )
        if params and params.pop("payconiq_qr", False):
            profile_id = self.env.company.payconiq_qr_profile_id
            # Build url that would be contained in QR code
            c_url = PAYCONIQ_URL + profile_id + "?"
            new_params = {
                "f": "PNG",
                "s": "S",
                "c": c_url + urllib.parse.urlencode(params),
            }
            response = requests.get(PAYCONIQ_QR_URL, params=new_params, stream=True)
            raw_image = response.raw
            img = Image.open(raw_image)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            myimage = buffer.getvalue()
            barcode = image_data_uri(base64.b64encode(myimage))
            return barcode
        return super()._get_qr_code_base64(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def _check_for_qr_code_errors(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        if qr_method == "payconiq_qr":
            if not self.env.company.payconiq_qr_profile_id:
                return _(
                    "You should provide a Payconiq Profile Id (Accounting > Settings > "
                    "Customer Payments > QR Codes"
                )
        return super()._check_for_qr_code_errors(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )
