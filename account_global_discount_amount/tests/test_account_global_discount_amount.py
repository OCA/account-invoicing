# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonCaseGlobalDiscount, CommonGlobalDiscount


class TestAccountGlobalDiscountAmount(CommonGlobalDiscount, CommonCaseGlobalDiscount):
    @classmethod
    def _create_record(cls, lines, discount_amount):
        # lines should be in the format [(price_unit, qty, tax, discount)]
        inv_lines = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "price_unit": price,
                    "quantity": qty,
                    "tax_ids": [(6, 0, tax.ids)],
                    "discount": discount_percent,
                },
            )
            for price, qty, tax, discount_percent in lines
        ]
        return cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": inv_lines,
                "global_discount_amount": discount_amount,
            }
        )

    def _check_discount_line(self, invoice, expected):
        self._check_invoice_discount_line(invoice, expected)

    def test_change_qty_on_line(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        record.with_context(check_move_validity=False).invoice_line_ids[1].quantity = 0
        self._check_discount_line(
            record,
            [
                (self.vat20, -10),
            ],
        )

    def test_refund(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        record = self._create_record(lines, 10)
        wizard = self.env["account.move.reversal"].create(
            {
                "refund_method": "refund",
                "move_ids": [(6, 0, record.ids)],
            }
        )
        action = wizard.reverse_moves()
        refund = self.env["account.move"].browse(action["res_id"])
        self._check_discount_line(
            refund,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )
