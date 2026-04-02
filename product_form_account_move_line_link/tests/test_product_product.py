from odoo import Command
from odoo.tests import new_test_user, tagged, users

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestProductProduct(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(
            cls.env,
            name="Simple User",
            login="simple",
            password="simple",
            email="simple@test.com",
            group_ids=[cls.env.ref("base.group_user").id],
            company_id=cls.env.company.id,
        )

    def setUp(self):
        super().setUp()
        self.product_template = self.env["product.template"].create(
            {"name": "Test Product Template"}
        )
        self.product = self.product_template.product_variant_id
        self.product_b = self.env["product.product"].create({"name": "Other Product"})
        self.product_with_bill = self.env["product.product"].create(
            {"name": "Product With Bill"}
        )
        self._create_bill_for_product(self.product_with_bill)
        self.account_move_line_model = self.env["account.move.line"]

    def _create_bill_for_product(self, product):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "invoice_date": "2024-05-01",
                "partner_id": self.partner_a.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "line",
                            "price_unit": 1000,
                            "quantity": 1,
                            "product_id": product.id,
                        }
                    )
                ],
            }
        )
        bill.action_post()

    def test_compute_account_move_lines_count(self):
        self._create_bill_for_product(self.product)

        self.product._compute_account_move_lines_count()
        self.product_b._compute_account_move_lines_count()
        self.product_template._compute_account_move_lines_count()
        self.assertEqual(self.product.account_move_lines_count, 1)
        self.assertEqual(self.product_b.account_move_lines_count, 0)
        self.assertEqual(self.product_template.account_move_lines_count, 1)

    @users("admin")
    def test_compute_account_move_lines_count_access(self):
        product = self.product_with_bill

        product._compute_account_move_lines_count()
        self.assertNotEqual(product.account_move_lines_count, 0)

    @users("simple")
    def test_compute_account_move_lines_count_no_access(self):
        product = self.product_with_bill

        product._compute_account_move_lines_count()
        self.assertNotEqual(product.account_move_lines_count, 0)
