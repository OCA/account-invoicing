from odoo import fields

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractLineInvoicingGroupingCriteria(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.GroupingCriteria = cls.env["contract.invoicing.grouping.criteria"]
        cls.note_and_discount_grouping_criteria = cls.GroupingCriteria.create(
            {
                "name": "Note",
                "field_ids": [
                    (
                        4,
                        cls.env.ref("contract.field_contract_contract__note").id,
                    )
                ],
                "line_field_ids": [
                    (
                        4,
                        cls.env.ref("contract.field_contract_line__discount").id,
                    )
                ],
            }
        )
        cls.discount_grouping_criteria = cls.GroupingCriteria.create(
            {
                "line_field_ids": [
                    (
                        4,
                        cls.env.ref("contract.field_contract_line__discount").id,
                    )
                ],
            }
        )
        # Put easy to test cl names and discount for grouping
        for i, c in enumerate([cls.contract, cls.contract2, cls.contract3]):
            for j, l in enumerate(c.contract_line_ids):
                l.name = "C%dL%d" % (i + 1, j + 1)
                if i == 0:
                    l.discount = 10
                elif i == 1:
                    l.discount = 20
                elif i == 2:
                    l.discount = (j + 1) * 10

        cls.contract.note = "Note 1"
        cls.contract2.note = "Note 2"
        cls.contract3.note = "Note 1"

    def test_invoicing_no_line_grouping_no_grouping(self):
        invoice_ids = (
            self.contract + self.contract2 + self.contract3
        )._recurring_create_invoice(date_ref=fields.Date.today())
        self.assertEqual(len(invoice_ids), 3)
        self.assertNotEqual(
            self.contract._get_related_invoices(),
            self.contract2._get_related_invoices(),
        )
        self.assertEqual(invoice_ids[0].invoice_origin, "Test Contract")
        self.assertEqual(invoice_ids[1].invoice_origin, "Test Contract 2")
        self.assertEqual(invoice_ids[2].invoice_origin, "Test Contract 3")
        self.assertEqual(invoice_ids[0].invoice_line_ids.mapped("name"), ["C1L1"])
        self.assertEqual(invoice_ids[1].invoice_line_ids.mapped("name"), ["C2L1"])
        self.assertEqual(
            invoice_ids[2].invoice_line_ids.mapped("name"), ["C3L1", "C3L2", "C3L3"]
        )

    def test_invoicing_grouping_contract_and_line_partner(self):
        self.partner.contract_invoicing_grouping_criteria_id = (
            self.note_and_discount_grouping_criteria.id
        )

        invoice_ids = (
            self.contract + self.contract2 + self.contract3
        )._recurring_create_invoice(date_ref=fields.Date.today())
        self.assertEqual(len(invoice_ids), 4)
        self.assertEqual(
            invoice_ids[0].invoice_origin, "Test Contract, Test Contract 3"
        )
        self.assertEqual(invoice_ids[1].invoice_origin, "Test Contract 3")
        self.assertEqual(invoice_ids[2].invoice_origin, "Test Contract 3")
        self.assertEqual(invoice_ids[3].invoice_origin, "Test Contract 2")
        self.assertEqual(
            invoice_ids[0].invoice_line_ids.mapped("name"),
            ["C1L1", "C3L1"],
        )
        self.assertEqual(invoice_ids[1].invoice_line_ids.mapped("name"), ["C3L2"])
        self.assertEqual(invoice_ids[2].invoice_line_ids.mapped("name"), ["C3L3"])
        self.assertEqual(invoice_ids[3].invoice_line_ids.mapped("name"), ["C2L1"])

    def test_invoicing_grouping_contract_and_line_company(self):
        self.contract.company_id.default_contract_invoicing_grouping_criteria_id = (
            self.note_and_discount_grouping_criteria.id
        )

        invoice_ids = (
            self.contract + self.contract2 + self.contract3
        )._recurring_create_invoice(date_ref=fields.Date.today())
        self.assertEqual(len(invoice_ids), 4)
        self.assertEqual(
            invoice_ids[0].invoice_origin, "Test Contract, Test Contract 3"
        )
        self.assertEqual(invoice_ids[1].invoice_origin, "Test Contract 3")
        self.assertEqual(invoice_ids[2].invoice_origin, "Test Contract 3")
        self.assertEqual(invoice_ids[3].invoice_origin, "Test Contract 2")
        self.assertEqual(
            invoice_ids[0].invoice_line_ids.mapped("name"),
            ["C1L1", "C3L1"],
        )
        self.assertEqual(invoice_ids[1].invoice_line_ids.mapped("name"), ["C3L2"])
        self.assertEqual(invoice_ids[2].invoice_line_ids.mapped("name"), ["C3L3"])
        self.assertEqual(invoice_ids[3].invoice_line_ids.mapped("name"), ["C2L1"])

    def test_invoicing_grouping_line_partner(self):
        self.partner.contract_invoicing_grouping_criteria_id = (
            self.discount_grouping_criteria.id
        )

        invoice_ids = (
            self.contract + self.contract2 + self.contract3
        )._recurring_create_invoice(date_ref=fields.Date.today())
        self.assertEqual(len(invoice_ids), 3)
        self.assertEqual(
            invoice_ids[0].invoice_origin, "Test Contract, Test Contract 3"
        )
        self.assertEqual(
            invoice_ids[1].invoice_origin, "Test Contract 2, Test Contract 3"
        )
        self.assertEqual(invoice_ids[2].invoice_origin, "Test Contract 3")
        self.assertEqual(
            invoice_ids[0].invoice_line_ids.mapped("name"),
            ["C1L1", "C3L1"],
        )
        self.assertEqual(
            invoice_ids[1].invoice_line_ids.mapped("name"), ["C2L1", "C3L2"]
        )
        self.assertEqual(invoice_ids[2].invoice_line_ids.mapped("name"), ["C3L3"])

    def test_invoicing_grouping_line_company(self):
        self.contract.company_id.default_contract_invoicing_grouping_criteria_id = (
            self.discount_grouping_criteria.id
        )

        invoice_ids = (
            self.contract + self.contract2 + self.contract3
        )._recurring_create_invoice(date_ref=fields.Date.today())
        self.assertEqual(len(invoice_ids), 3)
        self.assertEqual(
            invoice_ids[0].invoice_origin, "Test Contract, Test Contract 3"
        )
        self.assertEqual(
            invoice_ids[1].invoice_origin, "Test Contract 2, Test Contract 3"
        )
        self.assertEqual(invoice_ids[2].invoice_origin, "Test Contract 3")
        self.assertEqual(
            invoice_ids[0].invoice_line_ids.mapped("name"),
            ["C1L1", "C3L1"],
        )
        self.assertEqual(
            invoice_ids[1].invoice_line_ids.mapped("name"), ["C2L1", "C3L2"]
        )
        self.assertEqual(invoice_ids[2].invoice_line_ids.mapped("name"), ["C3L3"])
