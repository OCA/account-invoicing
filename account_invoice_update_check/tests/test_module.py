# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, at_install, post_install
from odoo.exceptions import ValidationError


@at_install(False)
@post_install(True)
class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.confirmed_invoice = self.env.ref("l10n_generic_coa.demo_invoice_followup")

    def test_confirmed_invoice(self):

        with self.assertRaises(ValidationError):
            # Writing on an accounting field should fail
            self.confirmed_invoice.mapped("invoice_line_ids").write({"price_unit": 555})

        # Writing on a non accounting field should work
        self.confirmed_invoice.mapped("invoice_line_ids").write({
            "origin": "TEST WRITE",
        })

    def test_draft_invoice(self):
        draft_invoice = self.confirmed_invoice.copy()

        # Writing on an accounting field should work
        draft_invoice.mapped("invoice_line_ids").write({"price_unit": 555})

        # Writing on a non accounting field should work
        draft_invoice.mapped("invoice_line_ids").write({"origin": "TEST WRITE"})
