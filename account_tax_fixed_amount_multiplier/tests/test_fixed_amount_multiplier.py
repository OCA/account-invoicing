# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestFixedAmountMultiplier(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dozen_uom = cls.env.ref("uom.product_uom_dozen")
        cls.unit_uom = cls.env.ref("uom.product_uom_unit")
        cls.box_uom = cls.env["uom.uom"].create(
            {
                "name": "Box of 10 Dozens",
                "relative_uom_id": cls.dozen_uom.id,
                "relative_factor": 10.0,
            }
        )
        cls.tax_multiplier_none = cls.env["account.tax"].create(
            {
                "name": "Fixed no multiplier",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "none",
                "type_tax_use": "sale",
            }
        )
        cls.tax_multiplier_quantity = cls.env["account.tax"].create(
            {
                "name": "Fixed quantity multiplier",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "quantity",
                "type_tax_use": "sale",
            }
        )
        cls.tax_multiplier_product_quantity = cls.env["account.tax"].create(
            {
                "name": "Fixed product_quantity multiplier",
                "amount_type": "fixed",
                "amount": 5.0,
                "fixed_amount_multiplier": "product_quantity",
                "type_tax_use": "sale",
            }
        )
        cls.tax_multiplier_product_weight = cls.env["account.tax"].create(
            {
                "name": "Fixed product_weight multiplier",
                "amount_type": "fixed",
                "amount": 3.0,
                "fixed_amount_multiplier": "product_weight",
                "type_tax_use": "sale",
            }
        )
        cls.product = cls._create_product(
            name="Test Product",
            lst_price=100.0,
            uom_id=cls.unit_uom.id,
        )

    def _get_tax_amount(self, invoice, tax):
        return abs(invoice.line_ids.filtered(lambda ln: ln.tax_line_id == tax).balance)

    # -------------------------------------------------------------------------
    # Multiplier = 'none'
    # -------------------------------------------------------------------------

    def test_multiplier_none(self):
        """Multiplier 'none': amount applied once per line, ignoring quantity."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=10,
            tax_ids=self.tax_multiplier_none,
        )
        # No qty multiplier: 1 * 5 = 5
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_none), 5.0, places=2
        )

    def test_multiplier_none_zero_quantity(self):
        """Test no multiplier applies the fixed amount once on zero quantity."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=0.0,
            tax_ids=self.tax_multiplier_none,
        )
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_none), 5.0, places=2
        )

    # -------------------------------------------------------------------------
    # Multiplier = 'quantity'
    # -------------------------------------------------------------------------

    def test_multiplier_quantity(self):
        """Multiplier 'quantity': line qty x amount (default behavior)."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=10,
            tax_ids=self.tax_multiplier_quantity,
        )
        # 10 * 5 = 50
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_quantity), 50.0, places=2
        )

    # -------------------------------------------------------------------------
    # Multiplier = 'product_quantity' (UoM conversion)
    # -------------------------------------------------------------------------

    def test_multiplier_product_quantity_same_uom(self):
        """Product UoM == line UoM -> no conversion, same as 'quantity'."""
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=10,
            tax_ids=self.tax_multiplier_product_quantity,
        )
        # Same UoM: 10 * 5 = 50
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_product_quantity),
            50.0,
            places=2,
        )

    def test_multiplier_product_quantity_dozen(self):
        """1 Dozen on a Units product -> qty converted to 12 units."""
        invoice = self._create_invoice(
            invoice_line_ids=[
                self._prepare_invoice_line(
                    product_id=self.product,
                    price_unit=100.0,
                    quantity=1,
                    tax_ids=self.tax_multiplier_product_quantity,
                    product_uom_id=self.dozen_uom,
                ),
            ],
        )
        # 1 dozen = 12 units -> 12 * 5 = 60
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_product_quantity),
            60.0,
            places=2,
        )

    def test_multiplier_product_quantity_hierarchy(self):
        """1 Box of 10 Dozens on a Units product -> 120 units."""
        invoice = self._create_invoice(
            invoice_line_ids=[
                self._prepare_invoice_line(
                    product_id=self.product,
                    price_unit=100.0,
                    quantity=1,
                    tax_ids=self.tax_multiplier_product_quantity,
                    product_uom_id=self.box_uom,
                ),
            ],
        )
        # 1 box = 10 dozens = 120 units -> 120 * 5 = 600
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_product_quantity),
            600.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Multiplier = 'product_weight'
    # -------------------------------------------------------------------------

    def test_multiplier_product_weight(self):
        """Product weight: product_quantity x product.weight x amount."""
        self.product.weight = 2.5
        invoice = self._create_invoice_one_line(
            product_id=self.product,
            price_unit=100.0,
            quantity=10,
            tax_ids=self.tax_multiplier_product_weight,
        )
        # 10 units * 2.5 kg/unit * 3.0 = 75
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_product_weight),
            75.0,
            places=2,
        )

    def test_multiplier_product_weight_dozen(self):
        """Product weight with UoM conversion: 1 dozen = 12 units."""
        self.product.weight = 2.5
        invoice = self._create_invoice(
            invoice_line_ids=[
                self._prepare_invoice_line(
                    product_id=self.product,
                    price_unit=100.0,
                    quantity=1,
                    tax_ids=self.tax_multiplier_product_weight,
                    product_uom_id=self.dozen_uom,
                ),
            ],
        )
        # 1 dozen = 12 units * 2.5 kg/unit * 3.0 = 90
        self.assertAlmostEqual(
            self._get_tax_amount(invoice, self.tax_multiplier_product_weight),
            90.0,
            places=2,
        )

    # -------------------------------------------------------------------------
    # Credit note
    # -------------------------------------------------------------------------

    def test_multiplier_product_quantity_credit_note(self):
        """UoM conversion works on credit notes."""
        credit_note = self._create_invoice(
            move_type="out_refund",
            invoice_line_ids=[
                self._prepare_invoice_line(
                    product_id=self.product,
                    price_unit=100.0,
                    quantity=1,
                    tax_ids=self.tax_multiplier_product_quantity,
                    product_uom_id=self.dozen_uom,
                ),
            ],
        )
        # 1 dozen = 12 units -> 12 * 5 = 60
        self.assertAlmostEqual(
            self._get_tax_amount(credit_note, self.tax_multiplier_product_quantity),
            60.0,
            places=2,
        )
