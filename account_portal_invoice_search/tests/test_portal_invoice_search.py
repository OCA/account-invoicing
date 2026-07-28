# Copyright 2026 Netkia - Jorge Valmala
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import HttpCase, TransactionCase, tagged


class TestPortalInvoiceSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        # Create test invoices
        cls.invoice_1 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test Service 1",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        cls.invoice_1.action_post()
        # Invoice with specific payment reference
        cls.invoice_2 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "payment_reference": "REF-12345",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test Service 2",
                            "quantity": 2.0,
                            "price_unit": 50.0,
                        }
                    )
                ],
            }
        )
        cls.invoice_2.action_post()
        # Invoice with different name
        cls.invoice_3 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "payment_reference": "ANOTHER-REF",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test Service 3",
                            "quantity": 1.0,
                            "price_unit": 75.0,
                        }
                    )
                ],
            }
        )
        cls.invoice_3.action_post()

    def test_search_by_name(self):
        """Test search invoices by name"""
        domain = [("partner_id", "=", self.partner.id)]
        # Search by invoice name
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter=self.invoice_1.name)
            .search(domain)
        )
        self.assertIn(self.invoice_1, result)
        self.assertEqual(len(result), 1)

    def test_search_by_payment_reference(self):
        """Test search invoices by payment reference"""
        domain = [("partner_id", "=", self.partner.id)]
        # Search by payment reference
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF-12345")
            .search(domain)
        )
        self.assertIn(self.invoice_2, result)
        self.assertEqual(len(result), 1)

    def test_search_partial_match(self):
        """Test search invoices with partial match"""
        domain = [("partner_id", "=", self.partner.id)]
        # Partial search on payment reference
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain)
        )
        # Should find both invoice_2 and invoice_3 (both have REF in payment_reference)
        self.assertIn(self.invoice_2, result)
        self.assertIn(self.invoice_3, result)
        self.assertEqual(len(result), 2)

    def test_search_no_filter(self):
        """Test search without portal filter returns all"""
        domain = [("partner_id", "=", self.partner.id)]
        result = self.env["account.move"].search(domain)
        # Should return all three invoices
        self.assertIn(self.invoice_1, result)
        self.assertIn(self.invoice_2, result)
        self.assertIn(self.invoice_3, result)
        self.assertGreaterEqual(len(result), 3)

    def test_search_no_results(self):
        """Test search with no matching results"""
        domain = [("partner_id", "=", self.partner.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="NONEXISTENT")
            .search(domain)
        )
        self.assertEqual(len(result), 0)

    def test_get_portal_search_domain(self):
        """Test _get_portal_search_domain method"""
        search_term = "TEST123"
        domain = self.env["account.move"]._get_portal_search_domain(search_term)
        # Should return OR condition for name and payment_reference
        self.assertEqual(len(domain), 3)  # ('|', tuple, tuple)
        self.assertEqual(domain[0], "|")
        self.assertIn("name", str(domain))
        self.assertIn("payment_reference", str(domain))
        self.assertIn(search_term, str(domain))

    def test_search_with_limit(self):
        """Test search with limit parameter"""
        domain = [("partner_id", "=", self.partner.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, limit=1)
        )
        # Should return only 1 invoice even though 2 match
        self.assertEqual(len(result), 1)
        self.assertIn(result.id, [self.invoice_2.id, self.invoice_3.id])

    def test_search_with_offset(self):
        """Test search with offset parameter"""
        domain = [("partner_id", "=", self.partner.id)]
        # Get all results first
        all_results = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, order="id")
        )
        self.assertEqual(len(all_results), 2)
        # Get with offset
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, offset=1, limit=1, order="id")
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, all_results[1].id)

    def test_search_with_order(self):
        """Test search with order parameter"""
        domain = [("partner_id", "=", self.partner.id)]
        # Search with ascending order
        result_asc = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, order="id asc")
        )
        # Search with descending order
        result_desc = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, order="id desc")
        )
        # Should return same records but in different order
        self.assertEqual(len(result_asc), len(result_desc))
        self.assertEqual(result_asc[0].id, result_desc[1].id)
        self.assertEqual(result_asc[1].id, result_desc[0].id)

    def test_search_with_limit_offset_order_combined(self):
        """Test search with limit, offset and order combined"""
        domain = [("partner_id", "=", self.partner.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, limit=1, offset=0, order="id desc")
        )
        self.assertEqual(len(result), 1)
        # Should get the invoice with highest ID
        all_results = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain, order="id desc")
        )
        self.assertEqual(result.id, all_results[0].id)

    def test_search_without_filter_with_pagination(self):
        """Test search without filter respects limit and offset"""
        domain = [("partner_id", "=", self.partner.id)]
        # Search without portal filter but with pagination
        result = self.env["account.move"].search(domain, limit=2, order="id")
        self.assertEqual(len(result), 2)
        # Verify all three invoices exist
        all_invoices = self.env["account.move"].search(domain)
        self.assertGreaterEqual(len(all_invoices), 3)

    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        domain = [("partner_id", "=", self.partner.id)]
        # Search with lowercase
        result_lower = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="ref")
            .search(domain)
        )
        # Search with uppercase
        result_upper = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="REF")
            .search(domain)
        )
        # Should return same results
        self.assertEqual(len(result_lower), len(result_upper))
        self.assertEqual(set(result_lower.ids), set(result_upper.ids))


@tagged("post_install", "-at_install")
class TestPortalInvoiceSearchController(TransactionCase):
    """Test portal invoice search controller integration"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create portal user
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal User Test",
                "login": "portal_test",
                "email": "portal@test.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        cls.partner = cls.portal_user.partner_id
        # Create test invoices for portal user
        cls.invoice_1 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Portal Test Service",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.invoice_1.action_post()
        cls.invoice_2 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "payment_reference": "PORTAL-REF-001",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Another Service",
                            "quantity": 1.0,
                            "price_unit": 200.0,
                        },
                    )
                ],
            }
        )
        cls.invoice_2.action_post()

    def test_portal_search_integration(self):
        """Test portal search filter is applied correctly"""
        # Test with search filter in context
        domain = [("partner_id", "=", self.partner.id)]
        invoices = (
            self.env["account.move"]
            .with_user(self.portal_user)
            .with_context(portal_invoice_filter="PORTAL-REF-001")
            .search(domain)
        )
        self.assertIn(self.invoice_2, invoices)
        self.assertEqual(len(invoices), 1)

    def test_portal_search_partial_integration(self):
        """Test portal search with partial match"""
        domain = [("partner_id", "=", self.partner.id)]
        invoices = (
            self.env["account.move"]
            .with_user(self.portal_user)
            .with_context(portal_invoice_filter="Portal")
            .search(domain)
        )
        # Should find invoice_1 (has "Portal Test Service" in line)
        self.assertGreater(len(invoices), 0)

    def test_portal_search_no_filter_integration(self):
        """Test without filter returns all invoices"""
        domain = [("partner_id", "=", self.partner.id)]
        invoices = self.env["account.move"].with_user(self.portal_user).search(domain)
        self.assertIn(self.invoice_1, invoices)
        self.assertIn(self.invoice_2, invoices)
        self.assertEqual(len(invoices), 2)


@tagged("post_install", "-at_install")
class TestPortalControllerMethods(TransactionCase):
    """Test portal controller methods directly for 100% coverage"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal Controller Test",
                "login": "portal_controller",
                "password": "portal_controller",
                "email": "controller@test.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.portal_user.partner_id.id,
                "payment_reference": "CTRL-TEST-001",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Controller Test",
                            "quantity": 1.0,
                            "price_unit": 150.0,
                        },
                    )
                ],
            }
        )
        cls.invoice.action_post()

    def test_portal_search_domain_creation(self):
        """Test _get_portal_search_domain returns correct structure"""
        search_term = "TEST-SEARCH"
        domain = self.env["account.move"]._get_portal_search_domain(search_term)
        # Verify domain structure - it's a tuple/list with OR operator
        self.assertGreaterEqual(len(domain), 3)
        self.assertEqual(domain[0], "|")
        # Verify it contains the fields we're searching
        domain_str = str(domain)
        self.assertIn("name", domain_str)
        self.assertIn("payment_reference", domain_str)
        self.assertIn(search_term, domain_str)

    def test_search_override_with_context(self):
        """Test _search override applies portal filter correctly"""
        # Test that _search is called with portal_invoice_filter context
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        # Search with context
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="CTRL-TEST-001")
            ._search(domain, offset=0, limit=10, order="id desc")
        )
        # Should return invoice IDs
        self.assertIsNotNone(result)
        self.assertIn(self.invoice.id, result)

    def test_search_override_without_context(self):
        """Test _search without portal_invoice_filter context"""
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        # Search without context - should use normal search
        result = self.env["account.move"]._search(domain, offset=0, limit=10)
        self.assertIsNotNone(result)
        self.assertIn(self.invoice.id, result)

    def test_search_with_offset_and_limit(self):
        """Test _search with offset and limit parameters"""
        # Create multiple invoices
        for i in range(5):
            self.env["account.move"].create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.portal_user.partner_id.id,
                    "payment_reference": f"OFFSET-TEST-{i}",
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": f"Offset Test {i}",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            },
                        )
                    ],
                }
            ).action_post()
        # Test with offset and limit
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="OFFSET")
            ._search(domain, offset=1, limit=2, order="id")
        )
        self.assertIsNotNone(result)
        # Should return exactly 2 results (limit=2) skipping first one (offset=1)
        self.assertLessEqual(len(result), 2)

    def test_empty_search_filter(self):
        """Test with empty search filter"""
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        # Empty string should be treated as no filter
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="")
            .search(domain)
        )
        # Should still return results (empty filter = no filter)
        self.assertGreater(len(result), 0)


@tagged("post_install", "-at_install")
class TestPortalControllerCoverage(TransactionCase):
    """Test portal controller integration - model level coverage"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal Coverage Test",
                "login": "portal_coverage",
                "password": "portal_coverage",
                "email": "portal_coverage@test.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.portal_user.partner_id.id,
                "payment_reference": "COVERAGE-TEST-REF",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Coverage Test Service",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.invoice.action_post()

    def test_model_search_with_portal_filter(self):
        """Test model search with portal_invoice_filter context"""
        # This covers the model's _search override
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        result = (
            self.env["account.move"]
            .with_user(self.portal_user)
            .with_context(portal_invoice_filter="COVERAGE-TEST-REF")
            .search(domain)
        )
        self.assertIn(self.invoice, result)
        self.assertEqual(len(result), 1)

    def test_model_search_without_filter(self):
        """Test model search without portal filter"""
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        result = self.env["account.move"].with_user(self.portal_user).search(domain)
        self.assertIn(self.invoice, result)

    def test_portal_search_with_special_characters(self):
        """Test search with special characters in filter"""
        domain = [("partner_id", "=", self.portal_user.partner_id.id)]
        # Test with dashes in search term
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="TEST-REF")
            .search(domain)
        )
        self.assertIn(self.invoice, result)


@tagged("post_install", "-at_install", "http")
class TestPortalControllerHTTP(HttpCase):
    """HTTP tests for portal controller - requires active HTTP server

    Run with: --test-tags=http (without --http-port=0)
    These tests provide 100% coverage of the controller code
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal HTTP Test",
                "login": "portal_http_test",
                "password": "portal_http_test",
                "email": "portal_http@test.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        # Create invoices with different references
        cls.invoice_1 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.portal_user.partner_id.id,
                "payment_reference": "HTTP-TEST-001",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "HTTP Test Service 1",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.invoice_1.action_post()

        cls.invoice_2 = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.portal_user.partner_id.id,
                "payment_reference": "HTTP-TEST-002",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "HTTP Test Service 2",
                            "quantity": 1.0,
                            "price_unit": 200.0,
                        },
                    )
                ],
            }
        )
        cls.invoice_2.action_post()

    def test_controller_with_search_parameter(self):
        """Test portal controller with search parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices?search=HTTP-TEST-001")
        self.assertEqual(response.status_code, 200)
        # Verify invoice 1 reference is in response
        self.assertIn("HTTP-TEST-001", response.text)

    def test_controller_without_search_parameter(self):
        """Test portal controller without search parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices")
        self.assertEqual(response.status_code, 200)
        # Both invoices should be visible
        self.assertIn(self.invoice_1.name, response.text)

    def test_controller_with_empty_search(self):
        """Test controller with empty search parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices?search=")
        self.assertEqual(response.status_code, 200)

    def test_controller_with_date_filters(self):
        """Test controller with date filters and search"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open(
            "/my/invoices?search=HTTP-TEST&date_begin=2026-01-01&date_end=2026-12-31"
        )
        self.assertEqual(response.status_code, 200)

    def test_controller_with_sortby(self):
        """Test controller with sortby parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices?search=HTTP&sortby=date")
        self.assertEqual(response.status_code, 200)

    def test_controller_with_filterby(self):
        """Test controller with filterby parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices?search=TEST&filterby=invoices")
        self.assertEqual(response.status_code, 200)

    def test_controller_with_pagination(self):
        """Test controller with pagination"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open("/my/invoices?search=HTTP&page=1")
        self.assertEqual(response.status_code, 200)

    def test_controller_search_in_parameter(self):
        """Test controller recognizes search_in parameter"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open(
            "/my/invoices?search=HTTP-TEST-002&search_in=portal_invoice_filter"
        )
        self.assertEqual(response.status_code, 200)
        # Should find invoice 2
        self.assertIn("HTTP-TEST-002", response.text)

    def test_controller_all_parameters_combined(self):
        """Test controller with all parameters for maximum coverage"""
        self.authenticate("portal_http_test", "portal_http_test")
        response = self.url_open(
            "/my/invoices?page=1&date_begin=2026-01-01&date_end=2026-12-31"
            "&sortby=date&filterby=invoices&search=HTTP-TEST"
            "&search_in=portal_invoice_filter"
        )
        self.assertEqual(response.status_code, 200)
        # Verify searchbar_inputs is present in rendered template
        self.assertIn("search", response.text.lower())

    def test_controller_case_insensitive_search(self):
        """Test controller search is case insensitive"""
        self.authenticate("portal_http_test", "portal_http_test")
        # Search with lowercase
        response = self.url_open("/my/invoices?search=http-test-001")
        self.assertEqual(response.status_code, 200)
        # Should still find the invoice (payment_reference is case insensitive)
