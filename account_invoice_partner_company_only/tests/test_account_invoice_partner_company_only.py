# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestPartnerCompanyOnly(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
            }
        )

        # Create an individual contact (not a company)
        cls.individual_contact = cls.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_company": False,
            }
        )

    def test_01_partner_domain_in_view(self):
        """Test that partner_id field has company-only domain in the view."""
        account_move = self.env["account.move"]
        view = self.env.ref("account.view_move_form")

        # Get the view arch with our module's modifications
        view_info = account_move.get_view(view_id=view.id)
        doc = etree.fromstring(view_info["arch"])

        # Find partner_id field in the view
        partner_fields = doc.xpath("//field[@name='partner_id']")

        # Check that the first partner_id field has the compayny type domain
        domain_found = False
        field = partner_fields[0]
        domain = field.get("domain")
        if "('is_company', '=', True)" in domain:
            domain_found = True

        self.assertTrue(
            domain_found,
            "partner_id field should have a domain restricting to companies",
        )

    def test_02_invoice_with_company(self):
        """Test creating an invoice with a company partner"""
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_company.id,
                "move_type": "out_invoice",
            }
        )
        self.assertEqual(
            invoice.partner_id,
            self.partner_company,
            "Invoice should be created with company partner",
        )

    def test_03_individual_contact_excluded_by_domain(self):
        """Test that individual contacts are excluded by the view domain.

        The domain restricts partner_id to companies only. A contact with
        is_company=False must not appear in a search using that domain.
        """
        domain = [("is_company", "=", True)]
        results = self.env["res.partner"].search(domain)
        self.assertIn(
            self.partner_company,
            results,
            "Company partner should be included in restricted domain search",
        )
        self.assertNotIn(
            self.individual_contact,
            results,
            "Individual contact should be excluded by the is_company domain",
        )
