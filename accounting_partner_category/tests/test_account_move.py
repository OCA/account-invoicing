from odoo.tests.common import Form, SavepointCase


class FilterAccountMoveByPartnerCategory(SavepointCase):
    @classmethod
    def _create_invoice(cls, partner):
        invoice_form = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice",
                tracking_disable=True,
            )
        )
        invoice_form.partner_id = partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product
            line_form.account_id = cls.income_account
        invoice = invoice_form.save()
        invoice.action_post()
        return invoice

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.tag_1 = cls.env["accounting.partner.category"].create(
            {
                "name": "tag 1",
            }
        )
        cls.tag_2 = cls.env["accounting.partner.category"].create(
            {
                "name": "tag 2",
            }
        )
        cls.tag_3 = cls.env["accounting.partner.category"].create(
            {
                "name": "tag 3",
            }
        )

        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "partner 1",
                "is_company": True,
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "partner 2",
                "is_company": True,
            }
        )
        cls.partner_3 = cls.env["res.partner"].create(
            {
                "name": "partner 3",
                "is_company": True,
            }
        )
        cls.partner_4 = cls.env["res.partner"].create(
            {
                "name": "partner 4",
                "is_company": True,
            }
        )

        cls.journal = cls.env["account.journal"].create(
            {"name": "Test sale journal", "code": "TSALE", "type": "sale"}
        )
        cls.product = cls.env["product.product"].create({"name": "Test product"})

        cls.income_account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )

        cls.partner_1.accounting_category_ids = cls.tag_1 | cls.tag_2
        cls.partner_2.accounting_category_ids = cls.tag_3
        cls.partner_3.accounting_category_ids = cls.tag_1 | cls.tag_2 | cls.tag_3
        cls.partner_4.accounting_category_ids = cls.env[
            "accounting.partner.category"
        ].browse()

        cls.invoice_p1 = cls._create_invoice(
            cls.env["res.partner"].create(
                {"name": "P1 child", "parent_id": cls.partner_1.id}
            )
        )
        cls.invoice_p2 = cls._create_invoice(cls.partner_2)
        cls.invoice_p3 = cls._create_invoice(cls.partner_3)
        cls.invoice_p4 = cls._create_invoice(cls.partner_4)

    def test_on_change(self):
        with Form(
            self.env["account.move"].with_context(
                default_move_type="out_invoice",
                tracking_disable=True,
            )
        ) as invoice_form:
            self.assertFalse(invoice_form.category_ids)
            invoice_form.partner_id = self.partner_1
            self.assertEqual(
                invoice_form.category_ids._get_ids(), (self.tag_1 | self.tag_2).ids
            )
            invoice_form.partner_id = self.partner_4
            self.assertFalse(invoice_form.category_ids)
            invoice_form.partner_id = self.partner_3
            invoice = invoice_form.save()
        self.assertEqual(invoice.category_ids, (self.tag_1 | self.tag_2 | self.tag_3))

    def test_inclusion(self):
        self.assertEqual(
            self.env["account.move"].search([("category_ids", "ilike", "tag 1")]),
            (self.invoice_p1 | self.invoice_p3),
        )

    def test_exclusion(self):
        search_result = self.env["account.move"].search(
            [("category_ids", "not ilike", "tag 1")]
        )
        expected = self.invoice_p2 | self.invoice_p4
        expected_not_present = self.invoice_p1 | self.invoice_p3
        self.assertTrue(
            set(expected.ids).issubset(set(search_result.ids)),
            f"Expect {expected} to be subset of {search_result} which is wrong at the moment.",
        )
        self.assertFalse(
            set(expected_not_present.ids).issubset(set(search_result.ids)),
            f"Expect {expected_not_present} shouldn't be found but present in "
            f"result search: {search_result}.",
        )

    def test_inclusion_and_exclusion(self):
        expected = self.invoice_p1
        expected_not_present = self.invoice_p2 | self.invoice_p3 | self.invoice_p4
        search_result = self.env["account.move"].search(
            [
                ("category_ids.name", "ilike", "tag 1"),
                ("category_ids.name", "not ilike", "tag 3"),
            ]
        )
        self.assertTrue(
            set(expected.ids).issubset(set(search_result.ids)),
            f"Expect {expected} to be subset of {search_result} which is wrong at the moment.",
        )
        self.assertFalse(
            set(expected_not_present.ids).issubset(set(search_result.ids)),
            f"Expect {expected_not_present} shouldn't be found but present "
            f"in result search: {search_result}.",
        )
