from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from .common import DefaultPurchaseJournalTest


class TestDefaultPurchaseJournal(DefaultPurchaseJournalTest):
    def test_default_purchase_journal01(self):
        """
        Test the Default Purchase Journal should set in journal of Bill
        whatever configured in default_purchase_journal_id of vendors.
        """
        # Should be changed by automatic on_change later
        invoice = self.AccountInvoice.create(
            {
                "partner_id": self.supplier_id.id,
                "move_type": "in_invoice",
            }
        )

        invoice._onchange_partner_id()
        self.assertEqual(invoice.journal_id.id, self.purchase_journal.id)

    def test_default_purchase_journal02(self):
        """
        Test the Default Purchase Journal should set in journal of Bill
        whatever configured in default_purchase_journal_id of vendors
        when we create a bill from purchase order.
        """
        self.po_vals = {
            "partner_id": self.supplier_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                )
            ],
        }

        self.po = self.PurchaseOrder.create(self.po_vals)
        self.po.button_confirm()
        self.invoice = self.AccountInvoice.create(
            {
                "partner_id": self.supplier_id.id,
                "purchase_id": self.po.id,
                # "account_id": self.supplier_id.property_account_payable_id.id,
                "move_type": "in_invoice",
            }
        )
        self.invoice._onchange_purchase_auto_complete()
        self.invoice._onchange_partner_id()

        self.assertEqual(self.invoice.journal_id.id, self.purchase_journal.id)
